# app/auth/routes.py
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from app.models import User, FarmProfile, BuyerProfile, SellerProfile
from app.utils.decorators import generate_reset_token, verify_reset_token
from app import db, bcrypt, mail

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
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        role = request.form.get("role")
        phone = request.form.get("phone", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("auth.register"))

        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_regex, email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        if not password or len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.register"))

        if phone and not (phone.isdigit() and len(phone) >= 10):
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("auth.register"))

        try:
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

            # 1. Create User instance
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_pw,
                role=role,
                phone=phone
            )
            db.session.add(user)
            db.session.flush()  # Generates user.id without committing transaction yet

            # 2. Dynamic Profile Initialization 🌟
            if role == 'buyer':
                buyer_profile = BuyerProfile(user_id=user.id)
                db.session.add(buyer_profile)
                
            elif role == 'seller':
                seller_profile = SellerProfile(user_id=user.id)
                db.session.add(seller_profile)  # FIXED: Was farm_profile
                
            elif role == 'both':
                buyer_profile = BuyerProfile(user_id=user.id)
                seller_profile = SellerProfile(user_id=user.id)
                db.session.add(buyer_profile)
                db.session.add(seller_profile)  # FIXED: Was farm_profile

            # 3. Commit entire transaction atomically
            db.session.commit()

            flash("Account created successfully!", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            print(f"Registration Error: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/login.html", body_class='page-login')


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


# FORGOT PASSWORD
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email.lower().strip()).first()

        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            # Send Email
            msg = Message(
                subject="Password Reset Request - Caffeine & Chaos",
                recipients=[user.email]
            )
            msg.body = f"""Hello {user.first_name or 'there'},

            You requested to reset your password. Click the link below to set a new password:

            {reset_url}

            This link will expire in 30 minutes. If you did not make this request, please ignore this email.
            """
            try:
                mail = current_app.extensions.get('mail')
                mail.send(msg)
                flash('A password reset link has been sent to your email.', 'info')
            except Exception as e:
                current_app.logger.error(f"Failed to send reset email: {e}")
                flash('Could not send reset email. Please try again later.', 'error')
        else:
            # Flashing info even if email is not found prevents email enumeration attacks
            flash('If an account exists with that email, a reset link has been sent.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


#  RESET PASSWORD ROUTE
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    
    if not email:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email.lower().strip()).first()

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return render_template('reset_password.html', token=token)

        # Update password hash
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
