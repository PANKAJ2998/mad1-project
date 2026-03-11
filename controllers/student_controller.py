from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db
from models.student import Student
from models.drive import PlacementDrive
from models.application import Application
from functools import wraps
from werkzeug.utils import secure_filename
import os
from datetime import date

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_only(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user._get_current_object()

        if not isinstance(user, Student):
            flash('Access denied! Student only.', 'danger')
            return redirect(url_for('auth.login'))

        return fn(*args, **kwargs)
    return wrapper

def is_allowed_file(filename):
    allowed_types = {'pdf', 'doc', 'docx'}

    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in allowed_types:
            return True

    return False

@student_bp.route('/dashboard')
@student_only
def dashboard():
    st = current_user
    today = date.today()

    approved_drvs = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today
    ).all()

    apps = Application.query.filter_by(student_id=st.id).all()

    app_drv_ids = []
    for app in apps:
        app_drv_ids.append(app.drive_id)

    return render_template('student/dashboard.html',
                         student=st,
                         approved_drives=approved_drvs,
                         applications=apps,
                         applied_drive_ids=app_drv_ids)

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_only
def profile():
    st = current_user

    if request.method == 'POST':
        st.name = request.form.get('name')
        st.department = request.form.get('department')
        st.phone = request.form.get('phone')

        if 'resume' in request.files:
            file = request.files['resume']

            if file and file.filename and is_allowed_file(file.filename):
                safe_filename = secure_filename(file.filename)
                f_name = f"student_{st.id}_{safe_filename}"
                folder = current_app.config['UPLOAD_FOLDER']
                file_path = os.path.join(folder, f_name)
                file.save(file_path)
                st.resume_filename = f_name
                flash('Resume uploaded successfully!', 'success')

            elif file and file.filename:
                flash('Invalid file type! Only PDF, DOC, DOCX allowed.', 'danger')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html', student=st)

@student_bp.route('/drives')
@student_only
def all_drives():
    today = date.today()

    avail_drvs = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today
    ).all()

    apps = Application.query.filter_by(student_id=current_user.id).all()

    app_drv_ids = []
    for app in apps:
        app_drv_ids.append(app.drive_id)

    return render_template('student/drives.html',
                         drives=avail_drvs,
                         applied_drive_ids=app_drv_ids)

@student_bp.route('/apply/<int:drive_id>')
@student_only
def apply(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)

    if drv.status != 'Approved':
        flash('This drive is not available for applications!', 'danger')
        return redirect(url_for('student.all_drives'))

    today = date.today()

    if drv.application_deadline < today:
        flash('Application deadline has passed!', 'danger')
        return redirect(url_for('student.all_drives'))

    existing = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()

    if existing:
        flash('You have already applied to this drive!', 'warning')
        return redirect(url_for('student.all_drives'))

    app = Application(
        student_id=current_user.id,
        drive_id=drive_id,
        status='Applied'
    )

    db.session.add(app)
    db.session.commit()
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/application_history')
@student_only
def app_history():
    apps = Application.query.filter_by(student_id=current_user.id).order_by(
        Application.application_date.desc()
    ).all()

    return render_template('student/application_history.html', applications=apps)
