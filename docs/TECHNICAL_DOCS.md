# Innovation Idea Tracker
## Technical Documentation

---

### University of Mustapha Benboulaid, Batna 2, Algeria
**Faculty of Mathematics and Computer Science**  
**Department of Computer Science**  
**Specialty**: Digital Transformation and Innovation  
**Module**: Innovation Management  
**Teacher**: Karima Saidi  
**Academic Year**: 2024-2025

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Schema](#4-database-schema)
5. [Project Structure](#5-project-structure)
6. [Installation Guide](#6-installation-guide)
7. [Configuration](#7-configuration)
8. [API Endpoints](#8-api-endpoints)
9. [Deployment](#9-deployment)
10. [Security Considerations](#10-security-considerations)

---

## 1. System Overview

The Innovation Idea Tracker is a full-stack web application that provides a platform for submitting, tracking, and evaluating innovative ideas within organizations or communities.

### Core Functionalities:
- User authentication with role-based access control
- Idea submission with categorization
- Voting system (upvote/downvote)
- Threaded comment system
- Administrative dashboard

---

## 2. Architecture

### Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
│                  HTML/CSS/JavaScript                     │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/HTTPS
┌─────────────────────────▼───────────────────────────────┐
│                    Flask Application                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Routes    │  │   Forms     │  │   Models    │     │
│  │  (app.py)   │  │ (forms.py)  │  │ (models.py) │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                          │                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Flask Extensions                    │   │
│  │  Flask-Login │ Flask-SQLAlchemy │ Flask-WTF     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │ SQLAlchemy ORM
┌─────────────────────────▼───────────────────────────────┐
│                    SQLite Database                       │
│         (ideas.db - can be upgraded to PostgreSQL)      │
└─────────────────────────────────────────────────────────┘
```

### Design Pattern: MVC (Model-View-Controller)
- **Model**: SQLAlchemy models (models.py)
- **View**: Jinja2 templates (templates/)
- **Controller**: Flask routes (app.py)

---

## 3. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | Flask | 3.0.0 |
| **Database ORM** | Flask-SQLAlchemy | 3.1.1 |
| **Authentication** | Flask-Login | 0.6.3 |
| **Form Handling** | Flask-WTF | 1.2.1 |
| **Form Validation** | WTForms | 3.1.1 |
| **Email Validation** | email-validator | 2.1.0 |
| **WSGI Server** | Gunicorn | 21.2.0 |
| **Database** | SQLite / PostgreSQL | - |
| **Frontend** | HTML5, CSS3, JavaScript | - |

---

## 4. Database Schema

### Entity Relationship Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Users     │     │    Ideas     │     │  Categories  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id (PK)      │────<│ submitter_id │     │ id (PK)      │
│ username     │     │ id (PK)      │>────│ name         │
│ email        │     │ title        │     │ icon         │
│ password_hash│     │ description  │     │ color        │
│ role         │     │ category_id  │>────│ is_predefined│
│ avatar_color │     │ status       │     └──────────────┘
│ created_at   │     │ created_at   │
└──────────────┘     └──────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│    Votes     │     │   Comments   │
├──────────────┤     ├──────────────┤
│ id (PK)      │     │ id (PK)      │
│ idea_id (FK) │     │ idea_id (FK) │
│ user_id (FK) │     │ user_id (FK) │
│ vote_type    │     │ parent_id(FK)│
│ created_at   │     │ content      │
└──────────────┘     │ created_at   │
                     └──────────────┘
```

### Table Definitions

#### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| username | VARCHAR(80) | UNIQUE, NOT NULL |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(256) | NOT NULL |
| role | VARCHAR(20) | DEFAULT 'submitter' |
| avatar_color | VARCHAR(7) | DEFAULT '#6366f1' |
| created_at | DATETIME | DEFAULT NOW |

#### Ideas Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| title | VARCHAR(200) | NOT NULL |
| description | TEXT | NOT NULL |
| category_id | INTEGER | FOREIGN KEY |
| submitter_id | INTEGER | FOREIGN KEY |
| status | VARCHAR(20) | DEFAULT 'pending' |
| created_at | DATETIME | DEFAULT NOW |

#### Votes Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| idea_id | INTEGER | FOREIGN KEY |
| user_id | INTEGER | FOREIGN KEY |
| vote_type | INTEGER | NOT NULL (+1/-1) |
| created_at | DATETIME | DEFAULT NOW |
| - | - | UNIQUE(idea_id, user_id) |

#### Comments Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| idea_id | INTEGER | FOREIGN KEY |
| user_id | INTEGER | FOREIGN KEY |
| parent_id | INTEGER | FOREIGN KEY (self) |
| content | TEXT | NOT NULL |
| created_at | DATETIME | DEFAULT NOW |

---

## 5. Project Structure

```
idea_tracker/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── forms.py               # WTForms form definitions
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment config
├── README.md              # Project overview
│
├── static/
│   └── style.css          # CSS styles (glassmorphism theme)
│
├── templates/
│   ├── base.html          # Base template with nav/footer
│   ├── auth/
│   │   ├── login.html     # Login page
│   │   └── register.html  # Registration page
│   ├── ideas/
│   │   ├── list.html      # Homepage with idea grid
│   │   ├── detail.html    # Single idea view
│   │   ├── submit.html    # Idea submission form
│   │   └── my_ideas.html  # User's submitted ideas
│   ├── admin/
│   │   └── dashboard.html # Admin control panel
│   └── errors/
│       ├── 404.html       # Not found page
│       └── 500.html       # Server error page
│
└── docs/
    ├── USER_GUIDE.md      # End-user documentation
    └── TECHNICAL_DOCS.md  # This file
```

---

## 6. Installation Guide

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Local Development Setup

```bash
# 1. Navigate to project directory
cd idea_tracker

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py

# 6. Open browser at http://localhost:5000
```

---

## 7. Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | 'dev-secret-key...' |
| DATABASE_URL | Database connection string | 'sqlite:///ideas.db' |

### Setting Environment Variables

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "your-secret-key-here"

# Linux/Mac
export SECRET_KEY="your-secret-key-here"
```

---

## 8. API Endpoints

### Authentication Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Idea Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage with ideas list |
| GET/POST | `/idea/new` | Submit new idea |
| GET | `/idea/<id>` | View idea details |
| POST | `/idea/<id>/vote` | Vote on idea (AJAX) |
| POST | `/idea/<id>/comment` | Add comment |
| POST | `/idea/<id>/delete` | Delete idea |
| GET | `/my-ideas` | View user's ideas |

### Admin Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin` | Admin dashboard |
| POST | `/admin/user/<id>/role` | Change user role |
| POST | `/admin/idea/<id>/status` | Change idea status |

---

## 9. Deployment

### Render.com Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/idea-tracker.git
   git push -u origin main
   ```

2. **Create Render Web Service**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render auto-detects `render.yaml`

3. **Environment Variables (Set in Render)**
   - `SECRET_KEY`: Auto-generated
   - `PYTHON_VERSION`: 3.11.0

4. **Deployment completes automatically**

### render.yaml Configuration

```yaml
services:
  - type: web
    name: innovation-idea-tracker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

## 10. Security Considerations

### Implemented Security Measures

1. **Password Hashing**
   - Werkzeug's `generate_password_hash()` with PBKDF2
   - Passwords never stored in plain text

2. **CSRF Protection**
   - Flask-WTF provides CSRF tokens for all forms

3. **Session Management**
   - Flask-Login manages secure user sessions

4. **Input Validation**
   - WTForms validates all user input
   - Length limits on all text fields

5. **Role-Based Access Control**
   - Three roles: submitter, reviewer, admin
   - Protected routes with `@login_required`

### Production Recommendations

- Use PostgreSQL instead of SQLite
- Set a strong `SECRET_KEY`
- Enable HTTPS
- Configure proper logging
- Regular database backups

---

## Appendix: Common Commands

```bash
# Run development server
python app.py

# Run with Gunicorn (production)
gunicorn app:app

# Create new database
python -c "from app import db; db.create_all()"

# Install new package
pip install package_name
pip freeze > requirements.txt
```

---

*Document Version: 1.0*  
*Last Updated: January 2025*
