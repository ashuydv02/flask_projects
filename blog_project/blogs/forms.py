from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User, Post


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm_password',
                                     validators=[DataRequired(), EqualTo('password'), Length(min=4)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This Username is already taken. please choose different one...')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This Email is already taken. please choose different one')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(), Length(min=4)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Now')
