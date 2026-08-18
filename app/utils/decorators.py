# app/utils/decorators.py — correct version
from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer

def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'seller':
            flash("Access restricted to sellers.", "warning")
            return redirect(url_for('main.home'))
        # ← NO setup check here — only checks role
        return f(*args, **kwargs)
    return decorated_function


def buyer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role not in ['buyer', 'both']:
            flash("Access restricted to buyers.", "warning")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash("Admin access required.", "warning")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
    

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        sub = getattr(current_user, 'subscription', None)
        if not sub or not sub.is_active():
            flash('An active seller subscription is required to perform this action.', 'warning')
            return redirect(url_for('seller.subscription_page'))
        return f(*args, **kwargs)
    return decorated_function


def generate_reset_token(user_email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    # Serializes the email address into an encrypted token
    return serializer.dumps(user_email, salt='password-reset-salt')

def verify_reset_token(token, expiration=1800):  # 1800 seconds = 30 minutes
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
        return email
    except Exception:
        return None