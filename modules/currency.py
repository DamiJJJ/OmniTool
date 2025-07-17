from flask import Blueprint, render_template, request
from datetime import datetime
import requests
import os
from extensions import db
from models import CurrencyLog

currency_bp = Blueprint('currency', __name__, template_folder='../templates')

CURRENCY_API_KEY = "922269b5be3a19a59538299e"

@currency_bp.route('/currency', methods=['GET', 'POST'])
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
