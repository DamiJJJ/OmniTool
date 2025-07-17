import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from datetime import datetime

app = Flask(__name__)

# --- SQLAlchemy Conf ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database models ---

class CurrencyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_currency = db.Column(db.String(10), nullable=False)
    to_currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    converted_amount = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<CurrencyLog {self.id}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo {self.id} - {self.description}>'

# --- API Keys ---

OPENWEATHER_API_KEY = "c58789670bdbb47b3015c68589ed18e3" #os.environ.get("OPENWEATHER_API_KEY")
CURRENCY_API_KEY = "922269b5be3a19a59538299e"

# --- TO-DO ROUTE --

@app.route('/todo', methods=['GET', 'POST'])
def todo_list():
    if request.method == 'POST':
        task_description = request.form.get('task')
        if task_description:
            new_task = Todo(description=task_description)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('todo_list'))
    
    todos = Todo.query.all()
    return render_template('todo.html', todos=todos)

@app.route('/todo/complete/<int:task_id>')
def complete_todo(task_id):
    task = Todo.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('todo_list'))

@app.route('/todo/delete/<int:task_id>')
def delete_todo(task_id):
    task = Todo.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('todo_list'))

# --- CURRENCY ROUTE ---

@app.route('/currency', methods=['GET', 'POST'])
def currency_converter():
    converted_amount = None
    error = None
    currencies = []
    
    try:
        symbols_url = f"https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(symbols_url)
        response.raise_for_status()
        data = response.json()
        currencies = sorted(data['rates'].keys())
    except requests.exceptions.RequestException as e:
        error = f"Failed to download currency list: {e}"
        print(f"Error fetching currency symbols: {e}")

    if request.method == 'POST':
        from_currency = request.form.get('from_currency')
        to_currency = request.form.get('to_currency')
        amount_str = request.form.get('amount')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("The amount must be positive.")
        except ValueError:
            error = "Invalid amount. Please enter a number."
            return render_template('currency.html', converted_amount=converted_amount, error=error, currencies=currencies)

        if from_currency and to_currency and amount:
            try:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                if to_currency in data['rates']:
                    exchange_rate = data['rates'][to_currency]
                    converted_amount = amount * exchange_rate

                    new_log = CurrencyLog(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        amount=amount,
                        converted_amount=converted_amount,
                        rate=exchange_rate
                    )
                    db.session.add(new_log)
                    db.session.commit()
                else:
                    error = "Invalid target currency."
            except requests.exceptions.RequestException as e:
                error = f"Currency API connection error: {e}"
                print(f"Error fetching exchange rate: {e}")
            except Exception as e:
                error = f"An error occurred while converting: {e}"
                print(f"General error in currency conversion: {e}")
        else:
            error = "Please fill all fields."

    currency_logs = CurrencyLog.query.order_by(CurrencyLog.timestamp.desc()).all()

    return render_template('currency.html', converted_amount=converted_amount, error=error, currencies=currencies, currency_logs=currency_logs)

# --- WEATHER ROUTE ---

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    error = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
            else:
                error = "Could not download weather forecast data. Check city name."
        else:
            error = "Please provide city name."
    return render_template('weather.html', weather_data=weather_data, error=error)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)