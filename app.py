from flask import Flask
from config import Config
from models import db, login_manager
from models.admin import Admin
from models.company import Company
from models.student import Student
import os

def setup_flask_app():
    my_app = Flask(__name__)
    my_app.config.from_object(Config)

    db.init_app(my_app)

    login_manager.init_app(my_app)
    login_manager.login_view = 'auth.user_login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def get_current_user(user_id):
        if not user_id:
            return None

        if user_id.startswith('admin_'):
            user_id_number = int(user_id.split('_')[1])
            admin_user = Admin.query.get(user_id_number)
            return admin_user
        elif user_id.startswith('company_'):
            user_id_number = int(user_id.split('_')[1])
            company_user = Company.query.get(user_id_number)
            return company_user
        elif user_id.startswith('student_'):
            user_id_number = int(user_id.split('_')[1])
            student_user = Student.query.get(user_id_number)
            return student_user

        return None

    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.company_controller import company_bp
    from controllers.student_controller import student_bp

    my_app.register_blueprint(auth_bp)
    my_app.register_blueprint(admin_bp)
    my_app.register_blueprint(company_bp)
    my_app.register_blueprint(student_bp)

    with my_app.app_context():
        db.create_all()

        default_admin = Admin.query.filter_by(username='admin').first()
        if not default_admin:
            default_admin = Admin(username='admin')
            default_admin.set_password('admin123')
            db.session.add(default_admin)
            db.session.commit()
            print("Default admin created: username=admin, password=admin123")

        upload_folder_path = my_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder_path):
            os.makedirs(upload_folder_path)

    return my_app

if __name__ == '__main__':
    flask_app = setup_flask_app()

    print("=" * 60)
    print("Placement Portal Application")
    print("=" * 60)
    print("Starting server at: http://127.0.0.1:5000")
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)

    flask_app.run(debug=True, host='127.0.0.1', port=5000)
