# ICTTrack - ICT Asset Management System

A modern Django-based web application for managing ICT assets and maintenance requests in an organization.

---

## Project Description

**ICTTrack** is an ICT Asset Management System that helps organizations:
- Track all ICT assets (laptops, desktops, printers, etc.)
- Manage maintenance requests efficiently
- Separate access between Admin and Staff

---

## Features

### For **Admin**:
- Add, Edit, and Delete ICT Assets
- View all maintenance tickets
- Manage system users
- Generate reports

### For **Staff**:
- View all assets
- Raise maintenance tickets when assets have issues
- Track the status of their tickets

### General:
- User Registration & Login
- Role-based access control
- Clean and responsive UI
- Ticket management system

---

##  Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Tailwind-inspired custom CSS

---

## Installation & Setup

1. **Clone the project**
   ```bash
   git clone <your-repo-url>
   cd ictsystem
   ##Creating Virtual Environment##
   python -m venv venv
venv\Scripts\activate   
**Install dependancies**
pip install django
**Run migrations**
python manage.py makemigrations
python manage.py migrate
**create superUser**
python manage.py createsuperuser
**Run server**
python manage.py runserver
**User role**
Username,Role,Password,Access
admin,Admin,admin,Full Access
Any Staff,Staff,(set during register),Limited Access
   **How to Use**
Admin adds all ICT assets first
Staff logs in → browses assets → raises ticket when there's an issue
Admin/Technician views tickets and updates their status
**Project Structure**
textictsystem/
├── assets/                 
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/assets/
├── static/
│   └── css/style.css
├── templates/
