from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.company import Company
from models.drive import PlacementDrive
from models.application import Application
from functools import wraps
from datetime import datetime

company_bp = Blueprint('company', __name__, url_prefix='/company')

def company_only(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user._get_current_object()

        if not isinstance(user, Company):
            flash('Access denied! Company only.', 'danger')
            return redirect(url_for('auth.login'))

        return fn(*args, **kwargs)
    return wrapper

@company_bp.route('/dashboard')
@company_only
def dashboard():
    co = current_user
    drv_list = PlacementDrive.query.filter_by(company_id=co.id).all()
    drv_cnt = len(drv_list)
    applicants_cnt = 0
    for drv in drv_list:
        app_cnt = len(drv.applications)
        applicants_cnt = applicants_cnt + app_cnt

    return render_template('company/dashboard.html',
                         company=co,
                         drives=drv_list,
                         total_drives=drv_cnt,
                         total_applicants=applicants_cnt)

@company_bp.route('/create_drive', methods=['GET', 'POST'])
@company_only
def create_drive():
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_desc = request.form.get('job_description')
        eligibility = request.form.get('eligibility')
        deadline = request.form.get('application_deadline')

        d_date = datetime.strptime(deadline, '%Y-%m-%d').date()

        drv = PlacementDrive(
            company_id=current_user.id,
            job_title=job_title,
            job_description=job_desc,
            eligibility=eligibility,
            application_deadline=d_date,
            status='Pending'
        )

        db.session.add(drv)
        db.session.commit()
        flash('Placement drive created successfully! Wait for admin approval.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/create_drive.html')

@company_bp.route('/edit_drive/<int:drive_id>', methods=['GET', 'POST'])
@company_only
def edit_drive(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)

    if drv.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        drv.job_title = request.form.get('job_title')
        drv.job_description = request.form.get('job_description')
        drv.eligibility = request.form.get('eligibility')

        deadline = request.form.get('application_deadline')
        d_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        drv.application_deadline = d_date

        db.session.commit()
        flash('Placement drive updated successfully!', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_drive.html', drive=drv)

@company_bp.route('/delete_drive/<int:drive_id>')
@company_only
def delete_drive(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)

    if drv.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.dashboard'))

    db.session.delete(drv)
    db.session.commit()
    flash('Placement drive deleted successfully!', 'success')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/close_drive/<int:drive_id>')
@company_only
def close_drive(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)

    if drv.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.dashboard'))

    drv.status = 'Closed'
    db.session.commit()
    flash('Placement drive closed successfully!', 'info')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive_applications/<int:drive_id>')
@company_only
def drive_apps(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)

    if drv.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.dashboard'))

    apps = Application.query.filter_by(drive_id=drive_id).all()

    return render_template('company/drive_applications.html',
                         drive=drv,
                         applications=apps)

@company_bp.route('/update_application/<int:application_id>/<string:status>')
@company_only
def update_app_status(application_id, status):
    app = Application.query.get_or_404(application_id)
    drv = PlacementDrive.query.get(app.drive_id)

    if drv.company_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('company.dashboard'))

    statuses = ['Shortlisted', 'Selected', 'Rejected']

    if status in statuses:
        app.status = status
        db.session.commit()
        flash(f'Application status updated to {status}!', 'success')
    else:
        flash('Invalid status!', 'danger')

    return redirect(url_for('company.drive_apps', drive_id=drv.id))
