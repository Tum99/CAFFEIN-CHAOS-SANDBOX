# app/auth/routes.py
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, FarmProfile
from app import db, bcrypt

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect_by_role(user)
        else:
            flash("Invalid email or password", "danger")

    return render_template("auth/login.html", body_class='page-login')

# Redirect based on role
def redirect_by_role(user):

    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif user.role == "buyer":
        return redirect(url_for("buyer.dashboard"))
    elif user.role == "seller":
        # Check if seller has a farm profile yet
        farm = FarmProfile.query.filter_by(user_id=user.id).first()
        if not farm or not farm.is_setup_complete:
            return redirect(url_for('seller.seller_setup'))
            
        return redirect(url_for("seller.dashboard"))
    else:
        return redirect(url_for("main.home"))




@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        phone = request.form.get("phone")

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("auth.register"))

        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_regex, email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.register"))

        if phone and not (phone.isdigit() and len(phone) >= 10):
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("auth.register"))

        
        try:
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

            user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_pw, role=role, phone=phone)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/login.html", body_class='page-login')


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
