from urllib.parse import urlparse

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, limiter
from models import User
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(
            f"Account created for {form.username.data}! You can now log in.", "success"
        )
        return redirect(url_for("auth.login"))
    return render_template("register.html", title="Register", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute;100 per hour")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                parsed = urlparse(next_page)
                if parsed.netloc or parsed.scheme:
                    next_page = None
            flash("Login successful!", "success")
            return redirect(next_page or url_for("index"))
        flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")
