import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from routes.auth_utils import validate_csrf

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('Invalid security token. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        errors = []
        if not name or len(name) < 2:
            errors.append('Please provide a valid full name (at least 2 characters).')
        if not email or not re.match(EMAIL_REGEX, email):
            errors.append('Please provide a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', name=name, email=email)

        # Check if user already exists
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash('An account with this email already exists. Please log in.', 'warning')
                    return render_template('register.html', name=name, email=email)

                # Insert new user with hashed password
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email, password_hash)
                )
                user_id = cursor.lastrowid
            db.commit()

            # Set user session
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash(f'Welcome, {name}! Your account has been created successfully.', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            db.rollback()
            flash(f'Database error occurred: {str(e)}', 'danger')
            return render_template('register.html', name=name, email=email)

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf(csrf_token):
            flash('Invalid security token. Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email)

        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f'Welcome back, {user["name"]}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid email or password. Please check your credentials.', 'danger')
                return render_template('login.html', email=email)
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
