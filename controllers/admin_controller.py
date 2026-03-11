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

def admin_only(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user._get_current_object()

        if not isinstance(user, Admin):
            flash('Access denied! Admin only.', 'danger')
            return redirect(url_for('auth.login'))

        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/dashboard')
@admin_only
def dashboard():
    students_cnt = Student.query.count()
    companies_cnt = Company.query.count()
    drives_cnt = PlacementDrive.query.count()
    apps_cnt = Application.query.count()
    pending_cos = Company.query.filter_by(approval_status='Pending').count()
    pending_drvs = PlacementDrive.query.filter_by(status='Pending').count()

    return render_template('admin/dashboard.html',
                         total_students=students_cnt,
                         total_companies=companies_cnt,
                         total_drives=drives_cnt,
                         total_applications=apps_cnt,
                         pending_companies=pending_cos,
                         pending_drives=pending_drvs)

@admin_bp.route('/companies')
@admin_only
def all_companies():
    q = request.args.get('search', '')

    if q:
        cos = Company.query.filter(
            Company.name.ilike(f'%{q}%')
        ).all()
    else:
        cos = Company.query.all()

    return render_template('admin/companies.html', companies=cos, search_query=q)

@admin_bp.route('/company/approve/<int:company_id>')
@admin_only
def approve_company(company_id):
    co = Company.query.get_or_404(company_id)
    co.approval_status = 'Approved'
    db.session.commit()
    flash(f'Company {co.name} approved successfully!', 'success')
    return redirect(url_for('admin.all_companies'))

@admin_bp.route('/company/reject/<int:company_id>')
@admin_only
def reject_company(company_id):
    co = Company.query.get_or_404(company_id)
    co.approval_status = 'Rejected'
    db.session.commit()
    flash(f'Company {co.name} rejected!', 'warning')
    return redirect(url_for('admin.all_companies'))

@admin_bp.route('/company/blacklist/<int:company_id>')
@admin_only
def toggle_co_blacklist(company_id):
    co = Company.query.get_or_404(company_id)
    co.is_blacklisted = not co.is_blacklisted
    db.session.commit()
    if co.is_blacklisted:
        flash(f'Company {co.name} has been blacklisted!', 'danger')
    else:
        flash(f'Company {co.name} has been removed from blacklist!', 'success')
    return redirect(url_for('admin.all_companies'))

@admin_bp.route('/students')
@admin_only
def all_students():
    q = request.args.get('search', '')
    cat = request.args.get('search_type', 'name')

    students = []

    if q:
        if cat == 'name':
            students = Student.query.filter(
                Student.name.ilike(f'%{q}%')
            ).all()
        elif cat == 'email':
            students = Student.query.filter(
                Student.email.ilike(f'%{q}%')
            ).all()
        elif cat == 'id':
            students = Student.query.filter_by(id=q).all()
        else:
            students = Student.query.all()
    else:
        students = Student.query.all()

    return render_template('admin/students.html',
                         students=students,
                         search_query=q,
                         search_type=cat)

@admin_bp.route('/student/blacklist/<int:student_id>')
@admin_only
def toggle_st_blacklist(student_id):
    st = Student.query.get_or_404(student_id)
    st.is_blacklisted = not st.is_blacklisted
    db.session.commit()
    if st.is_blacklisted:
        flash(f'Student {st.name} has been blacklisted!', 'danger')
    else:
        flash(f'Student {st.name} has been removed from blacklist!', 'success')
    return redirect(url_for('admin.all_students'))

@admin_bp.route('/drives')
@admin_only
def all_drives():
    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    return render_template('admin/drives.html', drives=drives)

@admin_bp.route('/drive/approve/<int:drive_id>')
@admin_only
def approve_drive(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)
    drv.status = 'Approved'
    db.session.commit()
    flash(f'Drive "{drv.job_title}" approved successfully!', 'success')
    return redirect(url_for('admin.all_drives'))

@admin_bp.route('/drive/reject/<int:drive_id>')
@admin_only
def reject_drive(drive_id):
    drv = PlacementDrive.query.get_or_404(drive_id)
    drv.status = 'Rejected'
    db.session.commit()
    flash(f'Drive "{drv.job_title}" rejected!', 'warning')
    return redirect(url_for('admin.all_drives'))

@admin_bp.route('/applications')
@admin_only
def all_apps():
    apps = Application.query.order_by(Application.application_date.desc()).all()
    return render_template('admin/applications.html', applications=apps)
