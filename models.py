from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='submitter')  # submitter, reviewer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_color = db.Column(db.String(7), default='#6366f1')  # Random avatar color
    
    # Relationships
    ideas = db.relationship('Idea', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_initials(self):
        return self.username[:2].upper()
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_reviewer(self):
        return self.role in ['reviewer', 'admin']


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='💡')
    color = db.Column(db.String(7), default='#6366f1')
    is_predefined = db.Column(db.Boolean, default=True)
    
    ideas = db.relationship('Idea', backref='category_rel', lazy='dynamic')


class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, implemented
    
    # Relationships
    votes = db.relationship('Vote', backref='idea', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='idea', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_vote_count(self):
        upvotes = Vote.query.filter_by(idea_id=self.id, vote_type=1).count()
        downvotes = Vote.query.filter_by(idea_id=self.id, vote_type=-1).count()
        return upvotes - downvotes
    
    def get_upvotes(self):
        return Vote.query.filter_by(idea_id=self.id, vote_type=1).count()
    
    def get_downvotes(self):
        return Vote.query.filter_by(idea_id=self.id, vote_type=-1).count()
    
    def user_vote(self, user_id):
        vote = Vote.query.filter_by(idea_id=self.id, user_id=user_id).first()
        return vote.vote_type if vote else 0
    
    def get_comment_count(self):
        return Comment.query.filter_by(idea_id=self.id).count()


class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('idea_id', 'user_id', name='unique_vote'),)


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for threaded comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def get_replies(self):
        return Comment.query.filter_by(parent_id=self.id).order_by(Comment.created_at.asc()).all()
    
    def time_ago(self):
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
