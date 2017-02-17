from flask import render_template, redirect, url_for, abort, flash, current_app, request
from . import admin
from .. import db
from ..models import User, Role, Post, Permission, Comment
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required


@admin.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('admin/moderate.html', comments=comments, pagination=pagination, page=page)


@admin.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@admin.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@admin.route('/admin/manager_user/', methods=['GET', 'POST'])
@login_required
@admin_required
def manager_user():
    users = User.query.all()
    if request.form.get('user'):
        id = request.form.get('user')
        user = User.query.filter_by(id=id).first()
        flash("删除成功")
        db.session.delete(user)
        return redirect(url_for('.manager_user', users=users))
    return render_template('admin/manager_user.html', users=users)


@admin.route('/admin/manager_article/', methods=['GET', 'POST'])
@login_required
@admin_required
def manager_article():
    posts = Post.query.all()
    if request.form.get('post'):
        id = request.form.get('post')
        post = Post.query.filter_by(id=id).first()
        db.session.delete(post)
        return redirect(url_for('.manager_article', posts=posts))
    return render_template('admin/manager_article.html', posts=posts)


@admin.route('/admin/manager_permission/', methods=['GET', 'POST'])
@login_required
@admin_required
def manager_permission():
    return render_template('admin/manager_permission.html')


@admin.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin/admin.html', users=users)





