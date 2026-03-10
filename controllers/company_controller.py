from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.company import Company
from models.drive import PlacementDrive
from models.application import Application
from functools import wraps
from datetime import datetime

company_bp = Blueprint('company', __name__, url_prefix='/company')

def check_if_company(function_to_wrap):
    @wraps(function_to_wrap)
    @login_required
    def wrapper_function(*args, **kwargs):
        logged_in_user = current_user._get_current_object()

        if not isinstance(logged_in_user, Company):
            flash('Access denied! Company only.', 'danger')
            return redirect(url_for('auth.user_login'))

        return function_to_wrap(*args, **kwargs)
    return wrapper_function

@company_bp.route('/dashboard')
@check_if_company
def company_dashboard_page():
    company_info = current_user

    company_drives = PlacementDrive.query.filter_by(company_id=company_info.id).all()

    total_drive_count = len(company_drives)

    total_applicant_count = 0

    for drive_item in company_drives:
        drive_applications_count = len(drive_item.applications)
        total_applicant_count = total_applicant_count + drive_applications_count

    return render_template('company/dashboard.html',
                         company=company_info,
                         drives=company_drives,
                         total_drives=total_drive_count,
                         total_applicants=total_applicant_count)

@company_bp.route('/create_drive', methods=['GET', 'POST'])
@check_if_company
def add_new_drive():
    if request.method == 'POST':
        job_title_text = request.form.get('job_title')
        job_description_text = request.form.get('job_description')
        eligibility_text = request.form.get('eligibility')
        deadline_text = request.form.get('application_deadline')

        deadline_date = datetime.strptime(deadline_text, '%Y-%m-%d').date()

        new_drive = PlacementDrive(
            company_id=current_user.id,
            job_title=job_title_text,
            job_description=job_description_text,
            eligibility=eligibility_text,
            application_deadline=deadline_date,
            status='Pending'
        )

        db.session.add(new_drive)

        db.session.commit()

        flash('Placement drive created successfully! Wait for admin approval.', 'success')

        return redirect(url_for('company.company_dashboard_page'))

    return render_template('company/create_drive.html')

@company_bp.route('/edit_drive/<int:drive_id>', methods=['GET', 'POST'])
@check_if_company
def modify_drive(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    if drive_record.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.company_dashboard_page'))

    if request.method == 'POST':
        drive_record.job_title = request.form.get('job_title')
        drive_record.job_description = request.form.get('job_description')
        drive_record.eligibility = request.form.get('eligibility')

        deadline_text = request.form.get('application_deadline')
        deadline_date = datetime.strptime(deadline_text, '%Y-%m-%d').date()
        drive_record.application_deadline = deadline_date

        db.session.commit()

        flash('Placement drive updated successfully!', 'success')

        return redirect(url_for('company.company_dashboard_page'))

    return render_template('company/edit_drive.html', drive=drive_record)

@company_bp.route('/delete_drive/<int:drive_id>')
@check_if_company
def remove_drive(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    if drive_record.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.company_dashboard_page'))

    db.session.delete(drive_record)

    db.session.commit()

    flash('Placement drive deleted successfully!', 'success')

    return redirect(url_for('company.company_dashboard_page'))

@company_bp.route('/close_drive/<int:drive_id>')
@check_if_company
def close_placement_drive(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    if drive_record.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.company_dashboard_page'))

    drive_record.status = 'Closed'

    db.session.commit()

    flash('Placement drive closed successfully!', 'info')

    return redirect(url_for('company.company_dashboard_page'))

@company_bp.route('/drive_applications/<int:drive_id>')
@check_if_company
def view_drive_applications(drive_id):
    drive_record = PlacementDrive.query.get_or_404(drive_id)

    if drive_record.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.company_dashboard_page'))

    application_list = Application.query.filter_by(drive_id=drive_id).all()

    return render_template('company/drive_applications.html',
                         drive=drive_record,
                         applications=application_list)

@company_bp.route('/update_application/<int:application_id>/<string:status>')
@check_if_company
def change_application_status(application_id, status):
    application_record = Application.query.get_or_404(application_id)

    drive_record = PlacementDrive.query.get(application_record.drive_id)

    if drive_record.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.company_dashboard_page'))

    valid_statuses = ['Shortlisted', 'Selected', 'Rejected']

    if status in valid_statuses:
        application_record.status = status

        db.session.commit()

        flash(f'Application status updated to {status}!', 'success')
    else:
        flash('Invalid status!', 'danger')

    return redirect(url_for('company.view_drive_applications', drive_id=drive_record.id))
