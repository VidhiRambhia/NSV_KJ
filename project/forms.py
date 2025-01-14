from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, IntegerField, RadioField, BooleanField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required, NumberRange, ValidationError
from project.models import User

class UserForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired(), Length(max = 30)])
	email = StringField('Email', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Done')

	def validateEmail(self, Email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email taken, enter a different one')


class LoginForm(FlaskForm):
	email = StringField('Email', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Log In')


class UpdateDetails(FlaskForm):
	name = StringField('Name', validators = [Length(max=30)])
	email = StringField('Email', validators = [Email()])
	password = PasswordField('New Password')
	submit = SubmitField('Update')

	def validateEmail(self, Email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email taken, enter a different one')

class PublishForm(FlaskForm):
	author = StringField('By', validators = [Length(max=1024)])
	title = StringField('Title of the Post', validators = [Length(max=2046)])
	text = StringField("What's the news?", validators = [Length(max=100000)])
	submit = SubmitField('Post it!')


