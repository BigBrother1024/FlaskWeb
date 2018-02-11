# coding=utf-8
from . import auth
from flask import render_template, redirect, url_for, flash, request
from .forms import LoginForm, RegisterionForm, ChangePasswordForm, ChangeEmailForm, \
    ForgetPasswordForm, ConfirmPasswordForm
from ..models import User, Message
from flask_login import login_required, logout_user, login_user, current_user
from .. import db
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('账号或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterionForm()
    send_user = User.query.filter_by(email='332627893@qq.com').first()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认账户', 'auth/email/confirm', user=user, token=token)
        flash('确认邮件已经发送')
        if send_user:
            message = Message(sender=send_user,
                              receiver=user,
                              body='欢迎来到博客')
            db.session.add(message)
            db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            if user.confirm(token):
                flash('你已认证')
                login_user(user, form.remember_me.data)
                return redirect(url_for('main.index'))
            else:
                flash('请认证你的账号')
                return redirect(url_for('auth.confirm', token=token))
        flash('账号或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/confirm')
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认账号', 'auth/email/confirm', user=current_user, token=token)
    flash('一个新的确认邮件已发出')
    return redirect(url_for('main.index'))


@auth.route('/settings/account', methods=['GET', 'POST'])
@login_required
def change_account():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            current_user.email = new_email
            current_user.confirmed = False
            token = current_user.generate_confirmation_token()
            send_email(new_email, '确认新账户', 'auth/email/confirm', user=current_user, token=token)
            flash('修改成功，确认邮件已发送')
            return redirect(url_for('auth.change_account'))
        else:
            flash('密码错误')
            return redirect(url_for('auth.change_account'))
    return render_template('auth/settings.html', form=form)


@auth.route('/settings/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('修改密码成功')
            return redirect(url_for('auth.change_password'))
        else:
            flash('旧密码错误，请重新输入')
            return redirect(url_for('auth.change_password'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/resetpassword', methods=['GET', 'POST'])
def reset_password_token():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(user.email, '重设密码', 'auth/email/reset', user=user, token=token)
        flash('重设密码邮件已发送')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/resetpassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ConfirmPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.confirm(token):
                user.password = form.password.data
                flash('重设密码成功')
                return redirect(url_for('auth.login'))
            else:
                flash('请输入你的账号')
                return redirect(url_for('auth.reset_password', token=token))
    return render_template('auth/reset_password.html', form=form)
