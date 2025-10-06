import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_projects = db.relationship('Project', backref='creator', lazy=True, foreign_keys='Project.creator_id')
    project_memberships = db.relationship('ProjectMember', backref='user', lazy=True)
    datasets = db.relationship('Dataset', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')
    datasets = db.relationship('Dataset', backref='project', lazy=True, cascade='all, delete-orphan')
    
    @staticmethod
    def generate_unique_code(length=8):
        """Generate a unique project code"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            if not Project.query.filter_by(code=code).first():
                return code
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'member_count': len(self.members)
        }

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # 'owner', 'member'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='unique_project_member'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))  # Legacy: for backward compatibility
    file_data = db.Column(db.LargeBinary)  # NEW: Store file content in database
    file_size = db.Column(db.Integer)  # NEW: Track file size
    columns_info = db.Column(db.JSON)
    preprocessing_info = db.Column(db.JSON)
    target_variable = db.Column(db.String(100))
    task_type = db.Column(db.String(50))  # 'classification' or 'regression'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    training_runs = db.relationship('TrainingRun', backref='dataset', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'columns_info': self.columns_info,
            'preprocessing_info': self.preprocessing_info,
            'target_variable': self.target_variable,
            'task_type': self.task_type,
            'uploaded_at': self.uploaded_at.isoformat()
        }

class TrainingRun(db.Model):
    __tablename__ = 'training_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    pipeline = db.Column(db.JSON)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'running', 'completed', 'failed'
    metrics = db.Column(db.JSON)
    model_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    results = db.relationship('ModelResult', backref='training_run', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'pipeline': self.pipeline,
            'status': self.status,
            'metrics': self.metrics,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class ModelResult(db.Model):
    __tablename__ = 'model_results'
    
    id = db.Column(db.Integer, primary_key=True)
    training_run_id = db.Column(db.Integer, db.ForeignKey('training_runs.id'), nullable=False)
    results_json = db.Column(db.JSON)
    interpretation = db.Column(db.Text)
    data_story = db.Column(db.Text)
    visualizations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'training_run_id': self.training_run_id,
            'results_json': self.results_json,
            'interpretation': self.interpretation,
            'data_story': self.data_story,
            'visualizations': self.visualizations,
            'created_at': self.created_at.isoformat()
        }

