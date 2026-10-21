from functools import wraps
import secrets
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    """
    Decorator to ensure user is logged in before accessing protected routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token():
    """
    Generate or retrieve a CSRF token for the current session.
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(24)
    return session['csrf_token']

def validate_csrf(token):
    """
    Validate the provided CSRF token against the session token.
    """
    session_token = session.get('csrf_token')
    if not session_token or not token or token != session_token:
        return False
    return True
