from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.admin import Admin
from models.company import Company
from models.student import Student
from models.drive import PlacementDrive
from models.application import Application
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_if_admin(function_to_wrap):
    @wraps(function_to_wrap)
    @login_required
    def wrapper_function(*args, **kwargs):
        logged_in_user = current_user._get_current_object()

        if not isinstance(logged_in_user, Admin):
            flash('Access denied! Admin only.', 'danger')
            return redirect(url_for('auth.user_login'))

        return function_to_wrap(*args, **kwargs)
    return wrapper_function

@admin_bp.route('/dashboard')
@check_if_admin
def admin_dashboard_page():
    total_student_count = Student.query.count()

    total_company_count = Company.query.count()

    total_drive_count = PlacementDrive.query.count()

    total_application_count = Application.query.count()

    pending_company_count = Company.query.filter_by(approval_status='Pending').count()

    pending_drive_count = PlacementDrive.query.filter_by(status='Pending').count()

    return render_template('admin/dashboard.html',
                         total_students=total_student_count,
                         total_companies=total_company_count,
                         total_drives=total_drive_count,
                         total_applications=total_application_count,
                         pending_companies=pending_company_count,
                         pending_drives=pending_drive_count)

@admin_bp.route('/companies')
@check_if_admin
def view_all_companies():
    search_text = request.args.get('search', '')

    if search_text:
        company_list = Company.query.filter(
            Company.name.ilike(f'%{search_text}%')
        ).all()
    else:
        company_list = Company.query.all()

    return render_template('admin/companies.html', companies=company_list, search_query=search_text)

@admin_bp.route('/company/approve/<int:company_id>')
@check_if_admin
def company_approval_action(company_id):
    company_record = Company.query.get_or_404(company_id)

    company_record.approval_status = 'Approved'

    db.session.commit()

    flash(f'Company {company_record.name} approved successfully!', 'success')

    return redirect(url_for('admin.view_all_companies'))

@admin_bp.route('/company/reject/<int:company_id>')
@check_if_admin
def company_rejection_action(company_id):
    company_record = Company.query.get_or_404(company_id)

    company_record.approval_status = 'Rejected'

    db.session.commit()

    flash(f'Company {company_record.name} rejected!', 'warning')

    return redirect(url_for('admin.view_all_companies'))

@admin_bp.route('/company/blacklist/<int:company_id>')
@check_if_admin
def toggle_company_blacklist(company_id):
    company_record = Company.query.get_or_404(company_id)

    company_record.is_blacklisted = not company_record.is_blacklisted

    db.session.commit()

    if company_record.is_blacklisted:
        flash(f'Company {company_record.name} has been blacklisted!', 'danger')
    else:
        flash(f'Company {company_record.name} has been removed from blacklist!', 'success')

    return redirect(url_for('admin.view_all_companies'))

@admin_bp.route('/students')
@check_if_admin
def view_all_students():
    search_text = request.args.get('search', '')
    search_category = request.args.get('search_type', 'name')

    student_list = []

    if search_text:
        if search_category == 'name':
            student_list = Student.query.filter(
                Student.name.ilike(f'%{search_text}%')
            ).all()
        elif search_category == 'email':
            student_list = Student.query.filter(
                Student.email.ilike(f'%{search_text}%')
            ).all()
        elif search_category == 'id':
            student_list = Student.query.filter_by(id=search_text).all()
        else:
            student_list = Student.query.all()
    else:
        student_list = Student.query.all()

    return render_template('admin/students.html',
                         students=student_list,
                         search_query=search_text,
                         search_type=search_category)

@admin_bp.route('/student/blacklist/<int:student_id>')
@check_if_admin
def toggle_student_blacklist(student_id):
    student_record = Student.query.get_or_404(student_id)

    student_record.is_blacklisted = not student_record.is_blacklisted

    db.session.commit()

    if student_record.is_blacklisted:
        flash(f'Student {student_record.name} has been blacklisted!', 'danger')
    else:
        flash(f'Student {student_record.name} has been removed from blacklist!', 'success')

    return redirect(url_for('admin.view_all_students'))

@admin_bp.route('/drives')
@check_if_admin
def view_all_drives():
    drive_list = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()

    return render_template('admin/drives.html', drives=drive_list)

@admin_bp.route('/drive/approve/<int:drive_id>')
@check_if_admin
def drive_approval_action(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    drive_record.status = 'Approved'

    db.session.commit()

    flash(f'Drive "{drive_record.job_title}" approved successfully!', 'success')

    return redirect(url_for('admin.view_all_drives'))

@admin_bp.route('/drive/reject/<int:drive_id>')
@check_if_admin
def drive_rejection_action(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    drive_record.status = 'Rejected'

    db.session.commit()

    flash(f'Drive "{drive_record.job_title}" rejected!', 'warning')

    return redirect(url_for('admin.view_all_drives'))

@admin_bp.route('/applications')
@check_if_admin
def view_all_applications():
    application_list = Application.query.order_by(Application.application_date.desc()).all()

    return render_template('admin/applications.html', applications=application_list)
