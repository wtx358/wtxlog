# -*- coding: utf-8 -*-

from . import account

from flask import flash, url_for, redirect, request, render_template
from flask.ext.login import login_user, logout_user, login_required, current_user

from ..utils.email import send_email
from ..models import db, User
from .forms import *


@account.route("/")
@login_required
def index():
    return render_template('index.html')


@account.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        errmsg, user = User.authenticate(form.email.data, form.password.data)
        if errmsg is None and isinstance(user, User):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('.index'))
        flash(errmsg)
    return render_template('login.html', form=form)


@account.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.index'))


@account.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('.login'))
    return render_template('register.html', form=form)


@account.route('/confirm/<token>/')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('.index'))


@account.route('/confirm/')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('.index'))


@account.route('/change-password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('.index'))
        else:
            flash('Invalid password.')
    return render_template("change_password.html", form=form)


@account.route('/reset/', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('.login'))
    return render_template('reset_password.html', form=form)


@account.route('/reset/<token>/', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('.login'))
        else:
            return redirect(url_for('.index'))
    return render_template('reset_password.html', form=form)


@account.route('/change-email/', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('.index'))
        else:
            flash('Invalid email or password.')
    return render_template("change_email.html", form=form)


@account.route('/change-email/<token>/')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('.index'))
