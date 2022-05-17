from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

'''
Форма авторизации с пользователем - содержит два поля: логин и пароль
'''
class LoginForm(FlaskForm):

    firstname = StringField('Firstname')
    surname = StringField('Surname')
    lastname = StringField('Lastname')

    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

'''
Форма регистрации с пользователем - содержит поля: логин и пароль, ФИО, повтор пароля, почта
'''
class RegistryForm(FlaskForm):

    firstname = StringField('Firstname')
    surname = StringField('Surname')
    lastname = StringField('Lastname')

    email = StringField('Email', validators=[DataRequired()])
    login = StringField('Login')

    password = PasswordField('Password')
    password_repeat = PasswordField('Repeat Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Registry')