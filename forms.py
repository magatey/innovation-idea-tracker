from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Category

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class IdeaForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=20, message='Description must be at least 20 characters')
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit Idea')
    
    def __init__(self, *args, **kwargs):
        super(IdeaForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, f"{c.icon} {c.name}") for c in Category.query.all()]


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=2, max=1000, message='Comment must be between 2 and 1000 characters')
    ])
    parent_id = HiddenField('Parent ID')
    submit = SubmitField('Post Comment')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    icon = StringField('Icon (emoji)', validators=[DataRequired()])
    submit = SubmitField('Add Category')
