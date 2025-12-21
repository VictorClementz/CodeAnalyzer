from flask import Blueprint, request, jsonify, current_app
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({"ok": True}), 200
        token = request.headers.get('Authorization') or request.headers.get('authorization')

        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            #Remove prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    #Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    #ceate new user
    user = User(email=email, name=name)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    }), 201

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200 
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name
    })