from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
import requests
import os
from models import CurrencyLog

currency_bp = Blueprint('currency', __name__, template_folder='../templates')

CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")
if not CURRENCY_API_KEY:
    flash("ERROR: NO CURRENCY_API_KEY VARIABLE. Please set it in your .env file.", "danger")
    print("ERROR: NO CURRENCY_API_KEY VARIABLE. Check .env file or environment configuration.")

@currency_bp.route('/currency', methods=['GET', 'POST'])
@login_required
def currency_converter():
    converted_amount = None
    currencies = []
    currency_logs = []
    
    try:
        symbols_url = f"https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(symbols_url)
        response.raise_for_status()
        data = response.json()
        currencies = sorted(data['rates'].keys())
    except requests.exceptions.RequestException as e:
        flash(f"Failed to load currency list: {e}. Check API key or internet connection.", "danger")
        print(f"Error fetching currency symbols: {e}")

    if request.method == 'POST':
        from_currency = request.form.get('from_currency')
        to_currency = request.form.get('to_currency')
        amount_str = request.form.get('amount')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("The amount must be positive.")
        except (ValueError, TypeError):
            flash("Invalid amount. Please enter a positive number.", "danger")
            if current_user.is_authenticated:
                currency_logs = CurrencyLog.query.filter_by(user_id=current_user.id).order_by(CurrencyLog.timestamp.desc()).limit(10).all()
            return render_template('currency.html', converted_amount=converted_amount, currencies=currencies, currency_logs=currency_logs)

        if not from_currency or not to_currency or not amount:
            flash("Please select both currencies and enter an amount.", "danger")
        else:
            try:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                if to_currency in data['rates']:
                    exchange_rate = data['rates'][to_currency]
                    converted_amount = amount * exchange_rate

                    if current_user.is_authenticated:
                        new_log = CurrencyLog(
                            user_id=current_user.id,
                            from_currency=from_currency,
                            to_currency=to_currency,
                            amount=amount,
                            converted_amount=converted_amount,
                            rate=exchange_rate
                        )
                        db.session.add(new_log)
                        db.session.commit()
                        flash(f"{amount:.2f} {from_currency} is {converted_amount:.2f} {to_currency}", "success")
                else:
                    flash("Invalid target currency.", "danger")
            except requests.exceptions.RequestException as e:
                flash(f"Currency API connection error: {e}. Check API key or internet connection.", "danger")
                print(f"Error fetching exchange rate: {e}")
            except Exception as e:
                flash(f"An error occurred while converting: {e}", "danger")
                print(f"General error in currency conversion: {e}")

    if current_user.is_authenticated:
        # Limit to 10 last conversions
        currency_logs = CurrencyLog.query.filter_by(user_id=current_user.id).order_by(CurrencyLog.timestamp.desc()).limit(10).all()

    return render_template('currency.html',
                           converted_amount=converted_amount,
                           currencies=currencies,
                           currency_logs=currency_logs,
                           from_currency=request.form.get('from_currency') if request.method == 'POST' else None,
                           to_currency=request.form.get('to_currency') if request.method == 'POST' else None,
                           amount=request.form.get('amount') if request.method == 'POST' else None)
