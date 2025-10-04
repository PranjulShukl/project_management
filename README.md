# Project Management System

A Django-based web application for managing employee project details with role-based access control. This system allows employees to submit and track their project details while giving directors oversight of all projects.

## Features

### User Management
- Two user roles: Employee and Director
- Secure authentication system
- Role-based access control
- Profile management with basic user information

### Project Management
- Complete project details tracking:
  - Project Name and Category
  - Tender Award Date and Completion Date
  - Company Information
  - Installation Location
  - Work Location (Office/Site)
  - Project Status and Description
- Project lifecycle management:
  - Draft state for editing
  - Submit feature to finalize project details
  - Read-only view after submission
- Filtering and search capabilities
- Pagination for large datasets

### Role-Based Access
- Employees can:
  - Create new projects
  - Edit draft projects
  - View their own projects
  - Submit projects for finalization
- Directors can:
  - View all employee projects
  - Access detailed project information
  - Use admin interface for user management
  - Filter and search across all projects

### Security Features
- CSRF protection
- Password validation and security
- Form validation and sanitization
- Secure session handling

### User Interface
- Responsive Bootstrap-based design
- Clean and intuitive navigation
- Mobile-friendly layout
- Interactive forms with validation
- Success/error message notifications

## Technology Stack

- Python 3.10+
- Django 5.2+
- PostgreSQL (Production) / SQLite (Development)
- Bootstrap 5
- Font Awesome icons
- Additional packages:
  - django-crispy-forms
  - django-filter
  - Pillow
  - python-dotenv

## Installation and Setup

1. Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install required packages:
```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

4. Run migrations:
```powershell
python manage.py migrate
```

5. Create a superuser (Director):
```powershell
python manage.py createsuperuser
```

6. Run the development server:
```powershell
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## Usage Guide

### Administrator/Director Setup
1. Log in to the admin interface using superuser credentials
2. Create user groups:
   - Navigate to Groups and create "Employee" and "Director" groups
   - Assign appropriate permissions to each group

### User Registration and Login
1. New employees can register at `/register/`
2. Login is available at `/login/`
3. Admins must assign appropriate groups to users

### Managing Projects
1. Creating a Project:
   - Click "New Project" button
   - Fill in all required fields
   - Save as draft or submit directly

2. Project States:
   - Draft: Can be edited and updated
   - Submitted: Read-only, cannot be modified

3. Project Views:
   - List View: Shows all accessible projects
   - Detail View: Shows complete project information
   - Edit View: Available for draft projects

### Search and Filter
1. Use the search bar to find specific projects
2. Filter projects by:
   - Status
   - Category
   - Date range
   - Location

## Security Considerations

### Production Deployment
1. Set `DEBUG=False` in production
2. Use strong, unique `SECRET_KEY`
3. Configure secure database connection
4. Set up proper `ALLOWED_HOSTS`
5. Enable HTTPS/SSL
6. Configure proper static file serving

### Data Protection
- Regular database backups
- Secure password policies
- Session timeout settings
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details