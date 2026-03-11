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

    def set_pwd(self, pwd):
        hsh = generate_password_hash(pwd)
        self.password_hash = hsh

    def verify_pwd(self, pwd):
        valid = check_password_hash(self.password_hash, pwd)
        return valid

    def get_id(self):
        uid = f'company_{self.id}'
        return uid

    def __repr__(self):
        return f'<Company {self.name}>'
