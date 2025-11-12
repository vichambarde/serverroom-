"""Authentication routes."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    """Landing page with login options."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both admin and users."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Check environment variables for admin credentials first
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Admin login via environment variables
        if username == admin_username and password == admin_password:
            session['user_id'] = 0  # Special ID for env admin
            session['username'] = username
            session['role'] = 'admin'
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        # Check database for users
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome, {user.username}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Logout the current user."""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.index'))

def login_required(role=None):
    """Decorator to require login for routes."""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('auth.login'))
            
            if role and session.get('role') != role:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('auth.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
