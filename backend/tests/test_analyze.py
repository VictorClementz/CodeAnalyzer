import pytest
from io import BytesIO


class TestAnalyzeRoute:
    """Test code analysis endpoint"""

    def test_analyze_without_auth(self, client, sample_code):
        """Test analysis endpoint requires authentication"""
        response = client.post('/analyze', json={
            'code': sample_code,
            'language': 'python'
        })

        assert response.status_code == 401

    def test_analyze_success(self, client, auth_headers, sample_code):
        """Test successful code analysis"""
        response = client.post('/analyze',
            json={
                'code': sample_code,
                'language': 'python',
                'save_results': False
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json

        assert 'readability_score' in data
        assert 'cyclomatic_complexity' in data
        assert 'maintainability_index' in data
        assert 'lines_of_code' in data
        assert 'comment_density' in data
        assert isinstance(data['readability_score'], (int, float))
        assert isinstance(data['lines_of_code'], int)

    def test_analyze_no_code(self, client, auth_headers):
        """Test analysis with no code provided"""
        response = client.post('/analyze',
            json={
                'language': 'python'
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert 'error' in response.json

    def test_analyze_with_save(self, client, auth_headers, sample_code):
        """Test analysis with save results enabled"""
        response = client.post('/analyze',
            json={
                'code': sample_code,
                'language': 'python',
                'save_results': True,
                'project_name': 'Test Project',
                'filename': 'test.py'
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json

        assert data.get('saved') is True
        assert 'analysis_id' in data
        assert 'readability_score' in data

    def test_analyze_creates_default_project(self, client, auth_headers, sample_code):
        """Test that analysis creates default project when no project name provided"""
        response = client.post('/analyze',
            json={
                'code': sample_code,
                'language': 'python',
                'save_results': True
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json.get('saved') is True

    def test_analyze_simple_code(self, client, auth_headers):
        """Test analysis of simple Python code"""
        simple_code = '''
def hello():
    """Say hello"""
    print("Hello, World!")
'''
        response = client.post('/analyze',
            json={
                'code': simple_code,
                'language': 'python'
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json

        assert data['cyclomatic_complexity'] >= 0
        assert data['lines_of_code'] > 0


class TestAnalyzeBatch:
    """Test batch file analysis endpoint"""

    def test_analyze_batch_without_auth(self, client):
        """Test batch analysis requires authentication"""
        data = {
            'language': 'python',
            'project_name': 'Test Project'
        }
        files = {
            'files': (BytesIO(b'print("test")'), 'test.py')
        }

        response = client.post('/analyze-batch',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 401

    def test_analyze_batch_no_files(self, client, auth_headers):
        """Test batch analysis with no files"""
        response = client.post('/analyze-batch',
            data={'language': 'python'},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert 'error' in response.json

    def test_analyze_batch_single_file(self, client, auth_headers):
        """Test batch analysis with single file"""
        code = b'''
def add(a, b):
    """Add two numbers"""
    return a + b
'''
        data = {
            'language': 'python',
            'project_name': 'Batch Test',
            'files': (BytesIO(code), 'math_utils.py')
        }

        response = client.post('/analyze-batch',
            data=data,
            content_type='multipart/form-data',
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json

        assert 'project_id' in result
        assert 'project_name' in result
        assert result['project_name'] == 'Batch Test'
        assert 'total_files' in result
        assert 'avg_readability' in result
        assert 'files' in result

    def test_analyze_batch_multiple_files(self, client, auth_headers):
        """Test batch analysis with multiple files"""
        file1 = b'def func1(): return 1'
        file2 = b'def func2(): return 2'

        data = {
            'language': 'python',
            'project_name': 'Multi File Test',
            'files': [
                (BytesIO(file1), 'file1.py'),
                (BytesIO(file2), 'file2.py')
            ]
        }

        response = client.post('/analyze-batch',
            data=data,
            content_type='multipart/form-data',
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json

        assert result['total_files'] >= 1
        assert len(result['files']) >= 1

    def test_analyze_batch_filters_by_extension(self, client, auth_headers):
        """Test that batch analysis filters files by extension"""
        py_file = b'def test(): pass'
        txt_file = b'This is a text file'

        data = {
            'language': 'python',
            'project_name': 'Filter Test',
            'files': [
                (BytesIO(py_file), 'test.py'),
                (BytesIO(txt_file), 'readme.txt')
            ]
        }

        response = client.post('/analyze-batch',
            data=data,
            content_type='multipart/form-data',
            headers=auth_headers
        )

        # Should only analyze the .py file
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            result = response.json
            # Only Python file should be analyzed
            assert all(f['filename'].endswith('.py') for f in result['files'] if 'error' not in f)
