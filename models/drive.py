from models import db
from datetime import datetime

class PlacementDrive(db.Model):

    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PlacementDrive {self.job_title}>'
