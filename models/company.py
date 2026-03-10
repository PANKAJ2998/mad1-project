from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Company(UserMixin, db.Model):

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='Pending')
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password_text):
        hashed_pwd = generate_password_hash(password_text)
        self.password_hash = hashed_pwd

    def check_password(self, password_text):
        is_correct = check_password_hash(self.password_hash, password_text)
        return is_correct

    def get_id(self):
        user_identifier = f'company_{self.id}'
        return user_identifier

    def __repr__(self):
        return f'<Company {self.name}>'
