# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import Required, Length, Regexp, Email
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    realname = StringField('真实名字', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('一句话介绍')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Email()])
    username = StringField('用户名', validators=[Required(), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, '用户名只能支持字母，数字，下划线')])
    confirmed = BooleanField('认证')
    role = SelectField('权限', coerce=int)
    realname = StringField('真实名字', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('一句话介绍')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


class PostForm(FlaskForm):
    body = PageDownField('此刻你的想法？', validators=[Required()])
    submit = SubmitField('发布')


class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('提交')


class MessageForm(FlaskForm):
    message = StringField('消息', validators=[Required()])
    submit = SubmitField('发送')
