import pytest
from models import db, User


class TestAuthRoutes:

    def test_signup_success(self, client):
        response = client.post('/auth/signup', json={
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'name': 'New User'
        })

        assert response.status_code == 201
        assert 'token' in response.json
        assert response.json['user']['email'] == 'newuser@example.com'
        assert response.json['user']['name'] == 'New User'

    def test_signup_missing_fields(self, client):
        response = client.post('/auth/signup', json={
            'email': 'incomplete@example.com'
        })

        assert response.status_code == 400
        assert 'error' in response.json

    def test_signup_duplicate_email(self, client, sample_user):
        response = client.post('/auth/signup', json={
            'email': 'sample@example.com',
            'password': 'password123',
            'name': 'Duplicate User'
        })

        assert response.status_code == 400
        assert 'already exists' in response.json['error'].lower()

    def test_login_success(self, client, sample_user):
        response = client.post('/auth/login', json={
            'email': 'sample@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert 'token' in response.json
        assert response.json['user']['email'] == 'sample@example.com'

    def test_login_wrong_password(self, client, sample_user):
        response = client.post('/auth/login', json={
            'email': 'sample@example.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        assert 'error' in response.json

    def test_login_nonexistent_user(self, client):
        response = client.post('/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })

        assert response.status_code == 401
        assert 'error' in response.json

    def test_get_current_user(self, client, auth_headers):
        response = client.get('/auth/me', headers=auth_headers)

        assert response.status_code == 200
        assert 'email' in response.json
        assert response.json['email'] == 'test@example.com'

    def test_get_current_user_no_token(self, client):
        response = client.get('/auth/me')

        assert response.status_code == 401
        assert 'error' in response.json

    def test_get_current_user_invalid_token(self, client):
        response = client.get('/auth/me', headers={
            'Authorization': 'Bearer invalid-token-xyz'
        })

        assert response.status_code == 401
        assert 'error' in response.json
