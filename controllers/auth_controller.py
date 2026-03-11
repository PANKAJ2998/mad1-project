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
def homepage():
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('email_or_username')
        pwd = request.form.get('password')
        user_type = request.form.get('user_type')

        user = None

        if user_type == 'admin':
            user = Admin.query.filter_by(username=login_id).first()

            if user:
                valid = user.verify_pwd(pwd)
                if valid:
                    login_user(user)
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Invalid admin credentials!', 'danger')
            else:
                flash('Invalid admin credentials!', 'danger')

        elif user_type == 'company':
            user = Company.query.filter_by(email=login_id).first()

            if user:
                if user.is_blacklisted:
                    flash('Your account has been blacklisted!', 'danger')
                elif user.approval_status != 'Approved':
                    flash('Your account is not yet approved by admin!', 'warning')
                else:
                    valid = user.verify_pwd(pwd)
                    if valid:
                        login_user(user)
                        flash('Login successful!', 'success')
                        return redirect(url_for('company.dashboard'))
                    else:
                        flash('Invalid company credentials!', 'danger')
            else:
                flash('Invalid company credentials!', 'danger')

        elif user_type == 'student':
            user = Student.query.filter_by(email=login_id).first()

            if user:
                if user.is_blacklisted:
                    flash('Your account has been blacklisted!', 'danger')
                else:
                    valid = user.verify_pwd(pwd)
                    if valid:
                        login_user(user)
                        flash('Login successful!', 'success')
                        return redirect(url_for('student.dashboard'))
                    else:
                        flash('Invalid student credentials!', 'danger')
            else:
                flash('Invalid student credentials!', 'danger')

    return render_template('login.html')

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pwd = request.form.get('password')
        dept = request.form.get('department')
        phone = request.form.get('phone')

        existing = Student.query.filter_by(email=email).first()

        if existing:
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register_student'))

        student = Student(
            name=name,
            email=email,
            department=dept,
            phone=phone
        )

        student.set_pwd(pwd)

        db.session.add(student)

        db.session.commit()

        flash('Registration successful! Please login.', 'success')

        return redirect(url_for('auth.login'))

    return render_template('register_student.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pwd = request.form.get('password')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')

        existing = Company.query.filter_by(email=email).first()

        if existing:
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register_company'))

        company = Company(
            name=name,
            email=email,
            hr_contact=hr_contact,
            website=website,
            approval_status='Pending'
        )

        company.set_pwd(pwd)

        db.session.add(company)

        db.session.commit()

        flash('Registration successful! Wait for admin approval to login.', 'success')

        return redirect(url_for('auth.login'))

    return render_template('register_company.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()

    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.homepage'))
