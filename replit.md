# Overview

This is a Flask-based appointment scheduling system for small to medium businesses. The system allows managing users with different permission levels, scheduling appointments between clients and employees, and handling various administrative tasks. It features a role-based permission system where master users have full access while restricted users have specific permissions. The application includes user management, employee/position management, appointment scheduling, reporting, and company configuration features.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database**: PostgreSQL with connection pooling and automatic reconnection handling
- **Authentication**: Flask-Login for session management with role-based access control
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **File Uploads**: Werkzeug for secure file handling with size limits (16MB max)

## Permission System
- **Master Users**: Full system access including user creation and system configuration
- **Restricted Users**: Granular permissions for specific operations (client management, employee management, scheduling, reporting)
- **Permission Decorators**: Custom decorators enforce access control at the route level

## Data Models
- **Usuario (User)**: Central user model with role-based permissions and authentication
- **Funcionario (Employee)**: Links users to positions for employee management
- **Cargo (Position)**: Job positions/roles for employees
- **Agendamento (Appointment)**: Core scheduling entity linking clients, employees, and time slots
- **ConfiguracaoEmpresa (Company Config)**: System branding and company information

## Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 for responsive UI
- **Static Assets**: Custom CSS and JavaScript for enhanced user experience
- **Responsive Design**: Mobile-first approach with collapsible sidebar navigation
- **File Management**: Secure upload handling for company logos and assets

## Security Features
- **Password Hashing**: Werkzeug security for password protection
- **Session Management**: Flask sessions with configurable secret keys
- **Access Control**: Route-level permission checking with role validation
- **File Security**: Secure filename handling and upload directory management

# External Dependencies

## Database
- **PostgreSQL**: Primary database with connection pooling via psycopg2
- **Environment Variables**: Database connection configured via PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

## Frontend Libraries
- **Bootstrap 5**: UI framework from CDN for responsive design
- **Font Awesome 6**: Icon library from CDN for consistent iconography
- **jQuery**: JavaScript library for DOM manipulation and AJAX (implied by templates)

## Python Packages
- **Flask**: Web framework and core dependencies
- **SQLAlchemy**: Database ORM and connection management
- **Flask-Login**: User session and authentication management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **psycopg2**: PostgreSQL database adapter
- **Werkzeug**: WSGI utilities and security helpers

## Infrastructure
- **ProxyFix**: Werkzeug middleware for handling proxy headers
- **Environment Configuration**: Runtime configuration via environment variables
- **Logging**: Python logging for debugging and monitoring