from models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password_text):
        hashed_pwd = generate_password_hash(password_text)
        self.password_hash = hashed_pwd

    def check_password(self, password_text):
        is_correct = check_password_hash(self.password_hash, password_text)
        return is_correct

    def get_id(self):
        user_identifier = f'admin_{self.id}'
        return user_identifier

    def __repr__(self):
        return f'<Admin {self.username}>'
