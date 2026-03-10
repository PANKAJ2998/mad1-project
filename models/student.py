from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Student(UserMixin, db.Model):

    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    resume_filename = db.Column(db.String(200))
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password_text):
        hashed_pwd = generate_password_hash(password_text)
        self.password_hash = hashed_pwd

    def check_password(self, password_text):
        is_correct = check_password_hash(self.password_hash, password_text)
        return is_correct

    def get_id(self):
        user_identifier = f'student_{self.id}'
        return user_identifier

    def __repr__(self):
        return f'<Student {self.name}>'
