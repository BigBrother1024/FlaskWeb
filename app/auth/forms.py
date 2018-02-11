# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Email, Required, Regexp, EqualTo
from ..models import User
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Email()])
    password = PasswordField('密码')
    remember_me = BooleanField('记住')
    submit = SubmitField('登录')


class RegisterionForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Email()])
    username = StringField('用户名', validators=[Required(), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, '用户名只能支持字母，数字，下划线')])
    password = PasswordField('密码', validators=[Required(), EqualTo('password2', message='密码不一致，请重新输入')])
    password2 = PasswordField('确认密码')
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[Required(), EqualTo('password2', message='密码不一致，请重新输入')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改')


class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱', validators=[Required(), Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('修改')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class ForgetPasswordForm(FlaskForm):
    email = StringField('你的邮箱', validators=[Required(), Email()])
    submit = SubmitField('重设密码')


class ConfirmPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Email()])
    password = PasswordField('新密码', validators=[Required(), EqualTo('password2', message='密码不一致，请重新输入')])
    password2 = PasswordField('确认密码')
    submit = SubmitField('提交')
