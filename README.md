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
ictsystem/
├── assets/                        # Main Django app
│   ├── migrations/
│   ├── templates/
│   │   └── assets/
│   │       ├── base.html          # Main layout (sidebar, topbar, flash messages)
│   │       ├── base_auth.html     # Auth layout (login/register, no sidebar)
│   │       ├── dashboard.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── assetlist.html
│   │       ├── add_asset.html
│   │       ├── asset_edit.html
│   │       ├── asset_confirm_delete.html
│   │       ├── ticket_list.html
│   │       ├── ticket_detail.html
│   │       ├── raise_ticket.html
│   │       ├── ticket_assign_tech.html
│   │       ├── ticket_start_repair.html
│   │       ├── ticket_resolve.html
│   │       ├── ticket_request_replacement.html
│   │       ├── finance_approval_list.html
│   │       ├── finance_approval_detail.html
│   │       ├── reports.html
│   │       └── users.html
│   ├── context_processors.py      # Sidebar notification badge counts
│   ├── forms.py                   # AssetForm, MaintenanceTicketForm
│   ├── models.py                  # Asset, MaintenanceTicket
│   ├── urls.py
│   └── views.py
├── ictsystem/                     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   └── css/
│       └── style.css
├── build.sh                       # Render build script
├── create_superuser.py            # Auto-creates admin on first deploy
├── manage.py
└── requirements.txt

---

## Ticket Workflow

| Step | Action | Who |
|---|---|---|
| 1 | Ticket Raised | Any logged-in user |
| 2 | Technician Assigned | Admin / Staff |
| 3 | Repair Started | Technician |
| 4 | Resolved or Replacement Requested | Technician / Admin |
| 5 | Finance Approval (if replacement needed) | Admin / Finance |
| 6 | Closed | System |

---

## Key URLs

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/login/` | Login |
| `/register/` | Register |
| `/assets/` | Asset List |
| `/add/` | Add Asset |
| `/tickets/` | Ticket List |
| `/ticket/<id>/` | Ticket Detail |
| `/ticket/<id>/assign/` | Assign Technician |
| `/ticket/<id>/start-repair/` | Start Repair |
| `/ticket/<id>/resolve/` | Resolve Ticket |
| `/ticket/<id>/request-replacement/` | Request Replacement |
| `/finance/approvals/` | Finance Approval List |
| `/finance/approval/<id>/` | Finance Approval Detail |
| `/reports/` | Reports |
| `/users/` | User Management |
| `/admin/` | Django Admin Panel |

---

## Production Deployment (Render)

### Environment Variables

Set these in your Render web service under **Environment**:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (generate a new one for production) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Render PostgreSQL internal connection URL |
| `DJANGO_SUPERUSER_USERNAME` | Admin username to auto-create on first deploy |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password |
| `DJANGO_SUPERUSER_EMAIL` | Admin email |

### Build & Start Commands

| Setting | Value |
|---|---|
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn ictsystem.wsgi:application` |



## License

This project was developed as an ICT Asset & Helpdesk Management System for internal departmental use.

---

## Author

Developed using Django, Tailwind CSS, and deployed on Render.