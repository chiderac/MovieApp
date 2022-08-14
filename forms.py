from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_mysqldb import MySQL
import MySQLdb.cursors


# Registration page  form
class RegistrationForm(FlaskForm):
    fullname = StringField('Fullname', validators=[DataRequired(),Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM users WHERE username = {self.username}")
        user = cursor.fetchone()
        if user:
            raise ValidationError('This username is already in use. Please choose another username!')
        
    def validate_email(self, email):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM users WHERE email = {self.email}")
        user = cursor.fetchone()
        if user:
            raise ValidationError('This email is already in use. Please choose another email!')

# Login Form to be used in the login page   
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

# Post Form to be used for the search page
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),Length(min=2, max=20)])
    submit = SubmitField('Search')