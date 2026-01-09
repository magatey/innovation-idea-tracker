# Innovation Idea Tracker

A modern web application for submitting, tracking, and evaluating innovative ideas. Built with Flask and featuring a premium glassmorphism dark theme.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- **User Authentication** - Secure registration and login with role-based access (submitter, reviewer, admin)
- **Idea Submission** - Submit ideas with title, description, and categories
- **Voting System** - Upvote/downvote ideas with real-time updates
- **Threaded Comments** - Nested comment system for idea discussions
- **Admin Dashboard** - Manage users, ideas, and categories
- **Modern UI** - Premium glassmorphism design with dark mode

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone or navigate to the project**
```bash
cd idea_tracker
```

2. **Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
```
http://localhost:5000
```

### Demo Login
- **Admin**: admin@example.com / admin123

## 📁 Project Structure

```
idea_tracker/
├── app.py              # Main Flask application
├── models.py           # Database models
├── forms.py            # WTForms
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── static/
│   └── style.css       # Premium CSS styles
└── templates/
    ├── base.html       # Base template
    ├── auth/           # Login/Register templates
    ├── ideas/          # Idea list/detail/submit
    ├── admin/          # Admin dashboard
    └── errors/         # Error pages
```

## 🌐 Deploy to Render (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Render will detect the `render.yaml` and deploy automatically

## 🎨 Screenshots

The application features a modern dark theme with:
- Animated gradient backgrounds
- Glassmorphism cards
- Smooth hover animations
- Responsive design for all devices

## 📝 User Roles

| Role | Permissions |
|------|-------------|
| **Submitter** | Submit ideas, vote, comment |
| **Reviewer** | All above + change idea status |
| **Admin** | All above + manage users and roles |

## 🛠️ Technologies

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom glassmorphism dark theme

## 📄 License

This project is created for educational purposes as part of the Innovation Management module at University of Mustapha Benboulaid, Batna 2.

---

**Module**: Innovation Management  
**Year**: Master 1 - Digital Transformation and Innovation  
**Teacher**: Karima Saidi  
**Academic Year**: 2024-2025
