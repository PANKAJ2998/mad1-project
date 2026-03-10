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

def check_if_student(function_to_wrap):
    @wraps(function_to_wrap)
    @login_required
    def wrapper_function(*args, **kwargs):
        logged_in_user = current_user._get_current_object()

        if not isinstance(logged_in_user, Student):
            flash('Access denied! Student only.', 'danger')
            return redirect(url_for('auth.user_login'))

        return function_to_wrap(*args, **kwargs)
    return wrapper_function

def check_file_type(file_name):
    allowed_types = {'pdf', 'doc', 'docx'}

    if '.' in file_name:
        file_extension = file_name.rsplit('.', 1)[1].lower()
        if file_extension in allowed_types:
            return True

    return False

@student_bp.route('/dashboard')
@check_if_student
def student_dashboard_page():
    student_info = current_user

    today_date = date.today()

    all_approved_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today_date
    ).all()

    student_applications = Application.query.filter_by(student_id=student_info.id).all()

    applied_drive_id_list = []
    for app in student_applications:
        applied_drive_id_list.append(app.drive_id)

    return render_template('student/dashboard.html',
                         student=student_info,
                         approved_drives=all_approved_drives,
                         applications=student_applications,
                         applied_drive_ids=applied_drive_id_list)

@student_bp.route('/profile', methods=['GET', 'POST'])
@check_if_student
def student_profile_page():
    student_info = current_user

    if request.method == 'POST':
        student_info.name = request.form.get('name')
        student_info.department = request.form.get('department')
        student_info.phone = request.form.get('phone')

        if 'resume' in request.files:
            uploaded_file = request.files['resume']

            if uploaded_file and uploaded_file.filename and check_file_type(uploaded_file.filename):
                safe_filename = secure_filename(uploaded_file.filename)

                final_filename = f"student_{student_info.id}_{safe_filename}"

                upload_folder = current_app.config['UPLOAD_FOLDER']

                complete_file_path = os.path.join(upload_folder, final_filename)

                uploaded_file.save(complete_file_path)

                student_info.resume_filename = final_filename

                flash('Resume uploaded successfully!', 'success')

            elif uploaded_file and uploaded_file.filename:
                flash('Invalid file type! Only PDF, DOC, DOCX allowed.', 'danger')

        db.session.commit()

        flash('Profile updated successfully!', 'success')

        return redirect(url_for('student.student_dashboard_page'))

    return render_template('student/profile.html', student=student_info)

@student_bp.route('/drives')
@check_if_student
def view_all_drives_page():
    today_date = date.today()

    available_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today_date
    ).all()

    student_applications = Application.query.filter_by(student_id=current_user.id).all()

    applied_drive_id_list = []
    for app in student_applications:
        applied_drive_id_list.append(app.drive_id)

    return render_template('student/drives.html',
                         drives=available_drives,
                         applied_drive_ids=applied_drive_id_list)

@student_bp.route('/apply/<int:drive_id>')
@check_if_student
def apply_to_drive(drive_id):
    drive_details = PlacementDrive.query.get_or_404(drive_id)

    if drive_details.status != 'Approved':
        flash('This drive is not available for applications!', 'danger')
        return redirect(url_for('student.view_all_drives_page'))

    today_date = date.today()

    if drive_details.application_deadline < today_date:
        flash('Application deadline has passed!', 'danger')
        return redirect(url_for('student.view_all_drives_page'))

    existing_app = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()

    if existing_app:
        flash('You have already applied to this drive!', 'warning')
        return redirect(url_for('student.view_all_drives_page'))

    new_application = Application(
        student_id=current_user.id,
        drive_id=drive_id,
        status='Applied'
    )

    db.session.add(new_application)

    db.session.commit()

    flash('Application submitted successfully!', 'success')

    return redirect(url_for('student.student_dashboard_page'))

@student_bp.route('/application_history')
@check_if_student
def view_application_history():
    student_applications = Application.query.filter_by(student_id=current_user.id).order_by(
        Application.application_date.desc()
    ).all()

    return render_template('student/application_history.html', applications=student_applications)
