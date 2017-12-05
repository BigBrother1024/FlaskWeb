#coding=utf-8
from flask import render_template, redirect, session, url_for, abort, flash, request, make_response, g
from flask_login import current_user, login_required
from . import main
from .. import db
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, MessageForm
from ..models import User, Role, Post, Permission, Comment, Reply, Message
from ..email import send_email
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    elif form.validate_on_submit():
        flash('请先登录')
        return redirect(url_for('.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=15, error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('修改成功')
        return redirect(url_for('main.user', username=current_user.username))
    form.realname.data = current_user.realname
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.realname = form.realname.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('修改成功')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.realname.data = user.realname
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / 20 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, error_out=True)
    comments = pagination.items
    return render_template('post.html', posts=[post], comments=comments, pagination=pagination, form=form)

@main.route('/comment/<int:id>', methods=['GET', 'POST'])
def comment(id):
    comment = Comment.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        reply = Reply(body=form.body.data,
                      comment=comment,
                      author=current_user._get_current_object())
        db.session.add(reply)
        return redirect(url_for('.comment', id=comment.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (comment.replies.count() - 1) / 20 + 1
    pagination = comment.replies.order_by(Reply.timestamp.asc()).paginate(page, error_out=True)
    replies = pagination.items
    return render_template('reply.html', comments=[comment], replies=replies, form=form)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if current_user == post.author or current_user.can(Permission.ADMINISTER):
        if form.validate_on_submit():
            post.body = form.body.data
            db.session.add(post)
            flash('编辑成功')
            return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    flash('关注成功！')
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    flash('取消成功！')
    return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, error_out=True)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='的关注者', endpoint='.followers', \
                           pagination=pagination, follows=follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, error_out=True)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='的关注', endpoint='.followed_by', \
                           pagination=pagination, follows=follows)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, error_out=True)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@main.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.values.get('keyword')
    if not keyword:
        return redirect(url_for('main.index'))
    posts = Post.search_post(keyword)

    return render_template('search.html', posts=posts, keyword=keyword)

@main.route('/search/posts/<keyword>')
def search_posts(keyword):
    posts = Post.search_post(keyword)
    return render_template('search.html', posts=posts, keyword=keyword)

@main.route('/search/comments/<keyword>')
def search_comments(keyword):
    pattern = '%{}%'.format(keyword)
    comments = Comment.query.filter(Comment.body.like(pattern)).order_by(Comment.timestamp.desc()).all()
    return render_template('search_comments.html', comments=comments, keyword=keyword)

@main.route('/search/users/<keyword>')
def search_users(keyword):
    pattern = '%{}%'.format(keyword)
    users = User.query.filter(User.username.like(pattern)).all()
    return render_template('search_users.html', users=users, keyword=keyword)

@main.route('/message/<username>', methods=['GET', 'POST'])
@login_required
def send_message(username):
    mess = request.args.get('message')
    user = User.query.filter_by(username=username).first()
    message = Message(sender=current_user,
                    receiver=user,
                    body=mess)
    db.session.add(message)
    db.session.commit()
    flash('发送成功')
    return redirect(url_for('main.user', username=username))

@main.route('/messages')
@login_required
def message():
    messages = current_user.messages.order_by(Message.timestamp.desc())
    return render_template('messages.html', messages=messages)

@main.route('/messages/read/<int:id>')
@login_required
def read_message(id):
    message = Message.query.get_or_404(id)
    message.read = True
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('main.message'))