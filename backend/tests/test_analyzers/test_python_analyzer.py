"""
Tests for PythonAnalyzer.
"""
import pytest
from infrastructure.analyzers.python_analyzer import PythonAnalyzer


class TestPythonAnalyzer:
    """Test the Python code analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create a Python analyzer instance."""
        return PythonAnalyzer()

    def test_simple_function(self, analyzer):
        """Test analysis of a simple Python function."""
        code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'python'
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] >= 0
        assert 0 <= results['maintainability_index'] <= 100
        assert 0 <= results['readability_score'] <= 100

    def test_complex_function(self, analyzer):
        """Test analysis of complex Python code with control flow."""
        code = """
def calculate_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1  # Has multiple branches
        assert results['max_nesting_depth'] >= 1

    def test_nested_loops(self, analyzer):
        """Test analysis of nested loops."""
        code = """
def nested_loops():
    for i in range(10):
        for j in range(10):
            if i == j:
                print(i, j)
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['max_nesting_depth'] >= 2
        assert results['cognitive_complexity'] > 0

    def test_comments_detection(self, analyzer):
        """Test comment density calculation."""
        code = """
# This is a comment
def foo():
    # Another comment
    # Yet another comment
    x = 1
    return x
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['comment_density'] > 0

    def test_naming_quality(self, analyzer):
        """Test naming quality metrics."""
        code = """
def my_function():
    very_long_descriptive_variable_name = 42
    x = 1
    temp = 2
    return very_long_descriptive_variable_name + x + temp
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['avg_name_length'] > 0
        assert isinstance(results['single_letter_warnings'], list)
        assert isinstance(results['unclear_name_flags'], list)

    def test_function_length(self, analyzer):
        """Test function length metrics."""
        code = """
def long_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    return x + y + z + a + b + c + d + e + f
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['avg_function_length'] > 0
        assert results['max_function_length'] > 0

    def test_empty_code(self, analyzer):
        """Test analysis of empty code."""
        code = ""
        results = analyzer.analyze(code)

        # Should handle gracefully
        assert results['lines_of_code'] == 0

    def test_syntax_error(self, analyzer):
        """Test handling of Python syntax errors."""
        code = """
def bad_function(
    print("Missing closing parenthesis"
"""
        results = analyzer.analyze(code)

        assert 'error' in results
        assert 'syntax error' in results['error'].lower()
        assert results['language'] == 'python'

    def test_all_metrics_present(self, analyzer):
        """Test that all expected metrics are present in results."""
        code = """
def sample_function(x, y):
    '''A sample function with documentation.'''
    if x > y:
        return x
    else:
        return y
"""
        results = analyzer.analyze(code)

        expected_metrics = [
            'lines_of_code',
            'cyclomatic_complexity',
            'maintainability_index',
            'readability_score',
            'comment_density',
            'avg_function_length',
            'max_function_length',
            'duplication_percentage',
            'avg_name_length',
            'max_nesting_depth',
            'avg_nesting_depth',
            'cognitive_complexity',
            'language'
        ]

        for metric in expected_metrics:
            assert metric in results, f"Missing metric: {metric}"

    def test_class_analysis(self, analyzer):
        """Test analysis of Python classes."""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] >= 0

    def test_get_thresholds(self, analyzer):
        """Test that analyzer provides Python-specific thresholds."""
        thresholds = analyzer.get_thresholds()

        assert isinstance(thresholds, dict)
        assert thresholds['max_function_length'] == 40
        assert thresholds['max_complexity'] == 10
        assert thresholds['ideal_avg_name_length'] == 12
        assert thresholds['min_comment_density'] == 15
