# Placement Portal Application

A comprehensive web-based placement portal system built with Flask, designed to manage campus recruitment activities for institutes, companies, and students.

## Features

### Admin Features
- Dashboard with statistics and charts
- Approve/Reject company registrations
- Approve/Reject placement drives
- Manage students and companies
- Blacklist users
- View all applications
- Search functionality for students and companies

### Company Features
- Registration with admin approval workflow
- Company dashboard with statistics
- Create, edit, and delete placement drives
- View applications for each drive
- Update application status (Shortlisted/Selected/Rejected)
- Close placement drives

### Student Features
- Student registration
- Profile management with resume upload
- Browse approved placement drives
- Apply to drives (no duplicate applications)
- Track application status
- View application history

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Jinja2, HTML, CSS, Bootstrap 5
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with session management
- **Charts**: Chart.js
- **Security**: Werkzeug password hashing

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. Navigate to the project directory:
```bash
cd projectname_2XfX00XXXX
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- **Windows**:
```bash
venv\Scripts\activate
```
- **Linux/Mac**:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

## Project Structure

```
projectname_2XfX00XXXX/
│
├── app.py                      # Main application file
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── admin.py
│   ├── company.py
│   ├── student.py
│   ├── drive.py
│   └── application.py
│
├── controllers/                # Route controllers
│   ├── auth_controller.py     # Authentication routes
│   ├── admin_controller.py    # Admin routes
│   ├── company_controller.py  # Company routes
│   └── student_controller.py  # Student routes
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register_student.html
│   ├── register_company.html
│   │
│   ├── admin/                  # Admin templates
│   │   ├── dashboard.html
│   │   ├── companies.html
│   │   ├── students.html
│   │   ├── drives.html
│   │   └── applications.html
│   │
│   ├── company/                # Company templates
│   │   ├── dashboard.html
│   │   ├── create_drive.html
│   │   ├── edit_drive.html
│   │   └── drive_applications.html
│   │
│   └── student/                # Student templates
│       ├── dashboard.html
│       ├── drives.html
│       ├── application_history.html
│       └── profile.html
│
└── static/                     # Static files
    ├── css/
    │   └── style.css
    ├── images/
    └── resumes/                # Uploaded resumes
```

## Database Schema

### Admin
- id, username, password_hash

### Company
- id, name, email, password_hash, hr_contact, website
- approval_status (Pending/Approved/Rejected)
- is_blacklisted, created_at

### Student
- id, name, email, password_hash, department, phone
- resume_filename, is_blacklisted, created_at

### PlacementDrive
- id, company_id (FK), job_title, job_description
- eligibility, application_deadline
- status (Pending/Approved/Closed), created_at

### Application
- id, student_id (FK), drive_id (FK)
- application_date, status (Applied/Shortlisted/Selected/Rejected)
- Unique constraint on (student_id, drive_id)

## User Workflows

### Company Workflow
1. Register on the platform
2. Wait for admin approval
3. Login after approval
4. Create placement drives
5. Wait for admin approval of drives
6. View and manage applications
7. Update application statuses

### Student Workflow
1. Register on the platform
2. Login immediately after registration
3. Update profile and upload resume
4. Browse approved placement drives
5. Apply to relevant drives
6. Track application status

### Admin Workflow
1. Login with default credentials
2. Review and approve company registrations
3. Review and approve placement drives
4. Monitor all activities
5. Manage users (blacklist if needed)

## Features Implemented

- Single login page for all user types
- Role-based access control
- Session management with Flask-Login
- Password hashing with Werkzeug
- File upload for student resumes
- Duplicate application prevention
- Admin approval workflows
- Blacklist functionality
- Search functionality
- Real-time statistics
- Responsive design with Bootstrap 5
- Interactive charts with Chart.js

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Login required decorators
- Role-based access control
- Secure file upload handling
- CSRF protection (Flask default)

## Notes

- The database is created automatically on first run
- Default admin user is created automatically
- Resume uploads are stored in `static/resumes/`
- SQLite database file: `placement_portal.db`
- All timestamps use UTC

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Edge
- Safari

## Support

For issues or questions, please refer to the project documentation.
