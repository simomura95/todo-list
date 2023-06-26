from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DecimalField
from wtforms.validators import InputRequired, URL, NumberRange, Email, EqualTo


# WTForm
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    # username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm password", validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class NewItemForm(FlaskForm):
    text = StringField("Text", validators=[InputRequired()])
    submit = SubmitField("Confirm")
