# app/utils/decorators.py — correct version
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

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