import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models import db, User, Project, ProjectFile, FileAnalysis


@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    from werkzeug.security import generate_password_hash

    with client.application.app_context():
        user = User(
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            name='Test User'
        )
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })

    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user(app):
    from werkzeug.security import generate_password_hash

    with app.app_context():
        user = User(
            email='sample@example.com',
            password_hash=generate_password_hash('password123'),
            name='Sample User'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_project(app, sample_user):
    with app.app_context():
        user = db.session.get(User, sample_user.id)
        project = Project(
            user_id=user.id,
            name='Test Project'
        )
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)
        return project


@pytest.fixture
def sample_code():
    """Return sample Python code for testing"""
    return '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers"""
    return a + b

def calculate_product(a, b):
    """Calculate the product of two numbers"""
    result = a * b
    return result

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(result)
        return result
'''
