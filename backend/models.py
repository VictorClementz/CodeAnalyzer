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

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    files = db.relationship('ProjectFile', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'file_count': len(self.files)
        }

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
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'language': self.language,
            'current_score': self.current_score,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None,
            'total_analyses': self.total_analyses,
            'project_id': self.project_id
        }

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

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'commit_hash': self.commit_hash,
            'commit_message': self.commit_message,
            'branch': self.branch,
            'readability_score': self.readability_score,
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'maintainability_index': self.maintainability_index,
            'lines_of_code': self.lines_of_code,
            'comment_density': self.comment_density,
            'duplication_percentage': self.duplication_percentage,
            'avg_name_length': self.avg_name_length,
            'max_nesting_depth': self.max_nesting_depth,
            'avg_nesting_depth': self.avg_nesting_depth,
            'cognitive_complexity': self.cognitive_complexity,
            'avg_function_length': self.avg_function_length,
            'max_function_length': self.max_function_length
        }