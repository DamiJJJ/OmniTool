import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

load_dotenv()

from extensions import db, migrate, login_manager
from models import CurrencyLog, Todo, User
from forms import RegistrationForm, LoginForm

# --- Import modules ---
from modules.weather import weather_bp
from modules.currency import currency_bp
from modules.todo import todo_bp

app = Flask(__name__)

# --- Basic Conf ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/set-theme', methods=['POST'])
def set_theme():
    data = request.get_json()
    theme = data.get('theme')
    if theme in ['dark', 'light']:
        session['theme'] = theme
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/')
def index():
    return render_template('index.html')

# --- Initialize extensions ---
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    """Callback function for Flask-Login to reload the user object from the user ID stored in the session."""
    return User.query.get(int(user_id))

# --- Register blueprints --
app.register_blueprint(weather_bp)
app.register_blueprint(currency_bp)
app.register_blueprint(todo_bp)

# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

@app.context_processor
def inject_theme():
    theme_setting = session.get('theme', 'light')
    return dict(current_theme_class=f"{theme_setting}-mode")

if __name__ == '__main__':
    #! Remove debug=True for production
    app.run(debug=True)