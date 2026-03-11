from flask import Flask
from config import Config
from models import db, login_manager
from models.admin import Admin
from models.company import Company
from models.student import Student
import os

def setup_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None

        if user_id.startswith('admin_'):
            uid = int(user_id.split('_')[1])
            return Admin.query.get(uid)
        elif user_id.startswith('company_'):
            uid = int(user_id.split('_')[1])
            return Company.query.get(uid)
        elif user_id.startswith('student_'):
            uid = int(user_id.split('_')[1])
            return Student.query.get(uid)

        return None

    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.company_controller import company_bp
    from controllers.student_controller import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()

        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_pwd('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username=admin, password=admin123")

        upload_path = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

    return app

if __name__ == '__main__':
    app = setup_app()

    print("=" * 60)
    print("Placement Portal Application")
    print("=" * 60)
    print("Starting server at: http://127.0.0.1:5000")
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)
