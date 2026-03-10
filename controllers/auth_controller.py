from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db
from models.admin import Admin
from models.company import Company
from models.student import Student
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def show_homepage():
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        user_email_or_username = request.form.get('email_or_username')
        user_password = request.form.get('password')
        selected_user_type = request.form.get('user_type')

        found_user = None

        if selected_user_type == 'admin':
            found_user = Admin.query.filter_by(username=user_email_or_username).first()

            if found_user:
                password_is_correct = found_user.check_password(user_password)
                if password_is_correct:
                    login_user(found_user)
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin.admin_dashboard_page'))
                else:
                    flash('Invalid admin credentials!', 'danger')
            else:
                flash('Invalid admin credentials!', 'danger')

        elif selected_user_type == 'company':
            found_user = Company.query.filter_by(email=user_email_or_username).first()

            if found_user:
                if found_user.is_blacklisted:
                    flash('Your account has been blacklisted!', 'danger')
                elif found_user.approval_status != 'Approved':
                    flash('Your account is not yet approved by admin!', 'warning')
                else:
                    password_is_correct = found_user.check_password(user_password)
                    if password_is_correct:
                        login_user(found_user)
                        flash('Login successful!', 'success')
                        return redirect(url_for('company.company_dashboard_page'))
                    else:
                        flash('Invalid company credentials!', 'danger')
            else:
                flash('Invalid company credentials!', 'danger')

        elif selected_user_type == 'student':
            found_user = Student.query.filter_by(email=user_email_or_username).first()

            if found_user:
                if found_user.is_blacklisted:
                    flash('Your account has been blacklisted!', 'danger')
                else:
                    password_is_correct = found_user.check_password(user_password)
                    if password_is_correct:
                        login_user(found_user)
                        flash('Login successful!', 'success')
                        return redirect(url_for('student.student_dashboard_page'))
                    else:
                        flash('Invalid student credentials!', 'danger')
            else:
                flash('Invalid student credentials!', 'danger')

    return render_template('login.html')

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def student_registration():
    if request.method == 'POST':
        student_name = request.form.get('name')
        student_email = request.form.get('email')
        student_password = request.form.get('password')
        student_department = request.form.get('department')
        student_phone = request.form.get('phone')

        existing_student_record = Student.query.filter_by(email=student_email).first()

        if existing_student_record:
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.student_registration'))

        new_student = Student(
            name=student_name,
            email=student_email,
            department=student_department,
            phone=student_phone
        )

        new_student.set_password(student_password)

        db.session.add(new_student)

        db.session.commit()

        flash('Registration successful! Please login.', 'success')

        return redirect(url_for('auth.user_login'))

    return render_template('register_student.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def company_registration():
    if request.method == 'POST':
        company_name = request.form.get('name')
        company_email = request.form.get('email')
        company_password = request.form.get('password')
        company_hr_contact = request.form.get('hr_contact')
        company_website = request.form.get('website')

        existing_company_record = Company.query.filter_by(email=company_email).first()

        if existing_company_record:
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.company_registration'))

        new_company = Company(
            name=company_name,
            email=company_email,
            hr_contact=company_hr_contact,
            website=company_website,
            approval_status='Pending'
        )

        new_company.set_password(company_password)

        db.session.add(new_company)

        db.session.commit()

        flash('Registration successful! Wait for admin approval to login.', 'success')

        return redirect(url_for('auth.user_login'))

    return render_template('register_company.html')

@auth_bp.route('/logout')
@login_required
def user_logout():
    logout_user()

    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.show_homepage'))
