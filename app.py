import os
from flask import Flask, render_template

from extensions import db 

from models import CurrencyLog, Todo 

from modules.weather import weather_bp
from modules.currency import currency_bp
from modules.todo import todo_bp

app = Flask(__name__)

# --- SQLAlchemy Conf ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Register blueprints --
app.register_blueprint(weather_bp)
app.register_blueprint(currency_bp)
app.register_blueprint(todo_bp)

@app.route('/')
def index():
    return render_template('index.html')