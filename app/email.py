from flask_mail import Message
from threading import Thread
from . import mail
from flask import render_template, current_app
from app import celery


@celery.task
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, sender='332627893@qq.com', recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    with app.app_context():
        mail.send(msg)
