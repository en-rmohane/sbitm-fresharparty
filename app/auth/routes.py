from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import User, Event
from app.extensions import db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('coordinator.dashboard'))

    event = Event.query.filter_by(is_active=True).first() or Event.query.first()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('This account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html', event=event)

            login_user(user, remember=True)
            flash(f'Welcome, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('coordinator.dashboard'))
        else:
            flash('Invalid username or password. Please verify your credentials.', 'danger')

    return render_template('auth/login.html', event=event)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('departments.landing'))

