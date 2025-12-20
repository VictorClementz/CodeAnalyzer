import pytest
from models import db, User, Project, ProjectFile, FileAnalysis
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class TestUserModel:
    def test_create_user(self, app):
        with app.app_context():
            user = User(
                email='testuser@example.com',
                password_hash=generate_password_hash('password123'),
                name='Test User'
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.email == 'testuser@example.com'
            assert user.name == 'Test User'
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)

    def test_user_password_hash(self, app):
        with app.app_context():
            password = 'securepassword123'
            user = User(
                email='hash@example.com',
                password_hash=generate_password_hash(password),
                name='Hash User'
            )
            db.session.add(user)
            db.session.commit()

            assert user.password_hash != password
            assert check_password_hash(user.password_hash, password)
            assert not check_password_hash(user.password_hash, 'wrongpassword')

    def test_user_unique_email(self, app, sample_user):
        with app.app_context():
            duplicate_user = User(
                email='sample@example.com',
                password_hash=generate_password_hash('password123'),
                name='Duplicate'
            )
            db.session.add(duplicate_user)

            with pytest.raises(Exception):
                db.session.commit()


class TestProjectModel:
    def test_create_project(self, app, sample_user):
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            project = Project(
                user_id=user.id,
                name='My Project'
            )
            db.session.add(project)
            db.session.commit()

            assert project.id is not None
            assert project.name == 'My Project'
            assert project.user_id == user.id
            assert project.created_at is not None

    def test_project_with_git_info(self, app, sample_user):
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            project = Project(
                user_id=user.id,
                name='Git Project',
                git_repo_path='/path/to/repo',
                git_remote_url='https://github.com/user/repo.git',
                auto_detect_git=True
            )
            db.session.add(project)
            db.session.commit()

            assert project.git_repo_path == '/path/to/repo'
            assert project.git_remote_url == 'https://github.com/user/repo.git'
            assert project.auto_detect_git is True

    def test_project_user_relationship(self, app, sample_user, sample_project):
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            projects = user.projects

            assert len(projects) >= 1
            assert any(p.id == sample_project.id for p in projects)


class TestProjectFileModel:
    def test_create_project_file(self, app, sample_project):
        with app.app_context():
            project = db.session.get(Project, sample_project.id)
            project_file = ProjectFile(
                project_id=project.id,
                filename='test.py',
                language='python',
                current_score=85.5,
                total_analyses=1
            )
            db.session.add(project_file)
            db.session.commit()

            assert project_file.id is not None
            assert project_file.filename == 'test.py'
            assert project_file.language == 'python'
            assert project_file.current_score == 85.5
            assert project_file.total_analyses == 1


class TestFileAnalysisModel:
    def test_create_file_analysis(self, app, sample_project):
        with app.app_context():
            project = db.session.get(Project, sample_project.id)
            project_file = ProjectFile(
                project_id=project.id,
                filename='analysis_test.py',
                language='python'
            )
            db.session.add(project_file)
            db.session.commit()

            analysis = FileAnalysis(
                file_id=project_file.id,
                commit_hash='abc123',
                branch='main',
                code_hash='def456',
                readability_score=75.0,
                cyclomatic_complexity=5,
                maintainability_index=70.5,
                lines_of_code=100,
                comment_density=15.0,
                duplication_percentage=5.0,
                avg_name_length=7.5,
                max_nesting_depth=3,
                avg_nesting_depth=1.5,
                cognitive_complexity=8,
                avg_function_length=15.0,
                max_function_length=30
            )
            db.session.add(analysis)
            db.session.commit()

            assert analysis.id is not None
            assert analysis.file_id == project_file.id
            assert analysis.readability_score == 75.0
            assert analysis.cyclomatic_complexity == 5
            assert analysis.commit_hash == 'abc123'
            assert analysis.branch == 'main'
            assert analysis.timestamp is not None
