from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    files = db.relationship('ProjectFile', backref='project', lazy=True, cascade='all, delete-orphan')

class ProjectFile(db.Model):
    __tablename__ = 'project_files'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    current_score = db.Column(db.Float)
    last_analyzed = db.Column(db.DateTime)
    total_analyses = db.Column(db.Integer, default=0)
    
    analyses = db.relationship('FileAnalysis', backref='file', lazy=True, cascade='all, delete-orphan')

class FileAnalysis(db.Model):
    __tablename__ = 'file_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('project_files.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Git info
    commit_hash = db.Column(db.String(40))
    commit_message = db.Column(db.Text)
    branch = db.Column(db.String(100))
    code_hash = db.Column(db.String(64))
    
    # Metrics
    readability_score = db.Column(db.Float)
    cyclomatic_complexity = db.Column(db.Float)
    maintainability_index = db.Column(db.Float)
    lines_of_code = db.Column(db.Integer)
    comment_density = db.Column(db.Float)
    duplication_percentage = db.Column(db.Float)
    avg_name_length = db.Column(db.Float)
    max_nesting_depth = db.Column(db.Integer)
    avg_nesting_depth = db.Column(db.Float)
    cognitive_complexity = db.Column(db.Integer)
    avg_function_length = db.Column(db.Float)
    max_function_length = db.Column(db.Integer)