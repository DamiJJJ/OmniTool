import os
from flask import Flask, render_template, request
import requests
import json
from datetime import datetime

app = Flask(__name__)

OPENWEATHER_API_KEY = "c58789670bdbb47b3015c68589ed18e3" #os.environ.get("OPENWEATHER_API_KEY")
CURRENCY_API_KEY = "922269b5be3a19a59538299e"

DB_FILE = 'currency_logs.json'

def load_currency_logs():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)
    
def save_currency_log(log_entry):
    logs = load_currency_logs()
    logs.append(log_entry)
    with open(DB_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

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
        error = f"Could not download the currency list: {e}"
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
            error = "Incorrect amount. Please enter the number."
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

                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'from_currency': from_currency,
                        'to_currency': to_currency,
                        'amount': amount,
                        'converted_amount': converted_amount,
                        'rate': exchange_rate
                    }
                    save_currency_log(log_entry)
                else:
                    error = "Incorrect target currency."
            except requests.exceptions.RequestException as e:
                error = f"Connection error with API: {e}"
                print(f"Error fetching exchange rate: {e}")
            except Exception as e:
                error = f"There was an error while converting: {e}"
                print(f"General error in currency conversion: {e}")
        else:
            error = "Please fill out all fields."

    currency_logs = load_currency_logs()

    return render_template('currency.html', converted_amount=converted_amount, error=error, currencies=currencies, currency_logs=currency_logs)

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
    app.run(debug=True)