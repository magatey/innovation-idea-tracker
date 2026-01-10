from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Idea, Vote, Comment, Category
from forms import RegistrationForm, LoginForm, IdeaForm, CommentForm, CategoryForm
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Handle DATABASE_URL - Render uses postgres:// but SQLAlchemy requires postgresql://
database_url = os.environ.get('DATABASE_URL', 'sqlite:///ideas.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============== UTILITY FUNCTIONS ==============

def init_categories():
    """Initialize predefined categories if they don't exist"""
    predefined = [
        {'name': 'Technology', 'icon': '💻', 'color': '#6366f1'},
        {'name': 'Process Improvement', 'icon': '⚙️', 'color': '#10b981'},
        {'name': 'Customer Experience', 'icon': '🎯', 'color': '#f59e0b'},
        {'name': 'Sustainability', 'icon': '🌱', 'color': '#22c55e'},
        {'name': 'Cost Reduction', 'icon': '💰', 'color': '#eab308'},
        {'name': 'Product Innovation', 'icon': '🚀', 'color': '#8b5cf6'},
        {'name': 'Employee Wellness', 'icon': '❤️', 'color': '#ef4444'},
        {'name': 'Digital Transformation', 'icon': '🔄', 'color': '#3b82f6'},
    ]
    
    for cat in predefined:
        if not Category.query.filter_by(name=cat['name']).first():
            new_cat = Category(name=cat['name'], icon=cat['icon'], color=cat['color'], is_predefined=True)
            db.session.add(new_cat)
    db.session.commit()

def create_admin_user():
    """Create an admin user if none exists"""
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            avatar_color='#ef4444'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# ============== AUTH ROUTES ==============

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        colors = ['#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#06b6d4']
        user = User(
            username=form.username.data,
            email=form.email.data,
            avatar_color=random.choice(colors)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ============== MAIN ROUTES ==============

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', None, type=int)
    sort_by = request.args.get('sort', 'newest')
    
    query = Idea.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if sort_by == 'popular':
        # Sort by vote count (subquery)
        ideas = query.all()
        ideas.sort(key=lambda x: x.get_vote_count(), reverse=True)
        # Manual pagination
        per_page = 9
        start = (page - 1) * per_page
        end = start + per_page
        paginated_ideas = ideas[start:end]
        total_pages = (len(ideas) + per_page - 1) // per_page
    elif sort_by == 'discussed':
        ideas = query.all()
        ideas.sort(key=lambda x: x.get_comment_count(), reverse=True)
        per_page = 9
        start = (page - 1) * per_page
        end = start + per_page
        paginated_ideas = ideas[start:end]
        total_pages = (len(ideas) + per_page - 1) // per_page
    else:  # newest
        pagination = query.order_by(Idea.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
        paginated_ideas = pagination.items
        total_pages = pagination.pages
    
    categories = Category.query.all()
    
    return render_template('ideas/list.html', 
                         ideas=paginated_ideas, 
                         categories=categories,
                         current_category=category_id,
                         current_sort=sort_by,
                         page=page,
                         total_pages=total_pages)

@app.route('/idea/new', methods=['GET', 'POST'])
@login_required
def submit_idea():
    form = IdeaForm()
    if form.validate_on_submit():
        idea = Idea(
            title=form.title.data,
            description=form.description.data,
            category_id=form.category_id.data,
            submitter_id=current_user.id
        )
        db.session.add(idea)
        db.session.commit()
        flash('Your idea has been submitted!', 'success')
        return redirect(url_for('view_idea', idea_id=idea.id))
    
    return render_template('ideas/submit.html', form=form)

@app.route('/idea/<int:idea_id>')
def view_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    form = CommentForm()
    
    # Get top-level comments (no parent)
    comments = Comment.query.filter_by(idea_id=idea_id, parent_id=None).order_by(Comment.created_at.desc()).all()
    
    return render_template('ideas/detail.html', idea=idea, form=form, comments=comments)

@app.route('/idea/<int:idea_id>/comment', methods=['POST'])
@login_required
def add_comment(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data else None
        comment = Comment(
            content=form.content.data,
            idea_id=idea_id,
            user_id=current_user.id,
            parent_id=int(parent_id) if parent_id else None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
    
    return redirect(url_for('view_idea', idea_id=idea_id))

@app.route('/idea/<int:idea_id>/vote', methods=['POST'])
@login_required
def vote(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    vote_type = request.json.get('vote_type', 1)
    
    existing_vote = Vote.query.filter_by(idea_id=idea_id, user_id=current_user.id).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote if clicking same button
            db.session.delete(existing_vote)
        else:
            # Change vote
            existing_vote.vote_type = vote_type
    else:
        # New vote
        new_vote = Vote(idea_id=idea_id, user_id=current_user.id, vote_type=vote_type)
        db.session.add(new_vote)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'vote_count': idea.get_vote_count(),
        'upvotes': idea.get_upvotes(),
        'downvotes': idea.get_downvotes(),
        'user_vote': idea.user_vote(current_user.id)
    })

@app.route('/idea/<int:idea_id>/delete', methods=['POST'])
@login_required
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    
    if idea.submitter_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this idea.', 'error')
        return redirect(url_for('view_idea', idea_id=idea_id))
    
    db.session.delete(idea)
    db.session.commit()
    flash('Idea deleted successfully.', 'success')
    return redirect(url_for('home'))

# ============== ADMIN ROUTES ==============

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    users = User.query.all()
    ideas = Idea.query.all()
    categories = Category.query.all()
    
    stats = {
        'total_users': len(users),
        'total_ideas': len(ideas),
        'total_votes': Vote.query.count(),
        'total_comments': Comment.query.count()
    }
    
    return render_template('admin/dashboard.html', stats=stats, users=users, ideas=ideas, categories=categories)

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
def change_user_role(user_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    user = User.query.get_or_404(user_id)
    new_role = request.json.get('role')
    
    if new_role in ['submitter', 'reviewer', 'admin']:
        user.role = new_role
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid role'})

@app.route('/admin/idea/<int:idea_id>/status', methods=['POST'])
@login_required
def change_idea_status(idea_id):
    if not current_user.is_reviewer():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    idea = Idea.query.get_or_404(idea_id)
    new_status = request.json.get('status')
    
    if new_status in ['pending', 'approved', 'rejected', 'implemented']:
        idea.status = new_status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid status'})

@app.route('/my-ideas')
@login_required
def my_ideas():
    ideas = Idea.query.filter_by(submitter_id=current_user.id).order_by(Idea.created_at.desc()).all()
    return render_template('ideas/my_ideas.html', ideas=ideas)

# ============== DOCUMENTATION ROUTES ==============

@app.route('/docs')
@app.route('/docs/')
def documentation():
    """Serve the documentation page"""
    return send_from_directory('docs', 'index.html')

@app.route('/docs/<path:filename>')
def docs_static(filename):
    """Serve static files for documentation (images, etc.)"""
    return send_from_directory('docs', filename)

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ============== INITIALIZATION ==============

with app.app_context():
    db.create_all()
    init_categories()
    create_admin_user()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
