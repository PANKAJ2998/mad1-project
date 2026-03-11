from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_pwd(self, pwd):
        hsh = generate_password_hash(pwd)
        self.password_hash = hsh

    def verify_pwd(self, pwd):
        valid = check_password_hash(self.password_hash, pwd)
        return valid

    def get_id(self):
        uid = f'admin_{self.id}'
        return uid

    def __repr__(self):
        return f'<Admin {self.username}>'
