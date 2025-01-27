from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     SelectField, FloatField, EmailField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegisterForm(FlaskForm):
    name = StringField('Adınız', validators=[DataRequired(),Length(min=2,max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(),Length(min=6)])
    confirm_password = PasswordField('Şifre Tekrar', validators=[DataRequired(),EqualTo('password')])
    customer_type = SelectField('Müşteri Türü', choices=[('Standard','Standard'),('Premium','Premium')], validators=[DataRequired()])
    budget = FloatField('Bütçe', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Kayıt Ol')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Şifre Sıfırlama Linki Gönder')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(),Length(min=6)])
    confirm_password = PasswordField('Yeni Şifre Tekrar', validators=[DataRequired(),EqualTo('new_password')])
    submit = SubmitField('Şifreyi Sıfırla')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[DataRequired()])
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(),Length(min=6)])
    confirm_password = PasswordField('Yeni Şifre Tekrar', validators=[DataRequired(),EqualTo('new_password')])
    submit = SubmitField('Şifreyi Değiştir')
