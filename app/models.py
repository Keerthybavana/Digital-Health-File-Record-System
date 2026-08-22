from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True, cascade="all, delete-orphan")
    activities = db.relationship('Activity', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(250), nullable=False)
    original_filename = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Prescription, Lab Report, Scan Report, Discharge Summary
    upload_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    qr_path = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"<Document {self.original_filename} - {self.category}>"

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Activity User:{self.user_id} - {self.activity}>"
