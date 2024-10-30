from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, DateField, BooleanField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Optional
from flask_ckeditor import CKEditor, CKEditorField


# Register User Form
class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pw_confirm', message='Passwords must '
                                                                                                   'match!')])
    pw_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords '
                                                                                                           'must match!'
                                                                                                           '')])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Sign me up!')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = CKEditorField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    completed = BooleanField('Completed')
    submit = SubmitField('Add Task')


class EditTodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = CKEditorField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    completed = BooleanField('Completed')
    submit = SubmitField('Save Changes')

