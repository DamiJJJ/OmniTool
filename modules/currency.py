import logging
import os
import requests
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user

from extensions import db
from models import CurrencyLog, FavoriteCurrencyPair

logger = logging.getLogger(__name__)

currency_bp = Blueprint("currency", __name__, template_folder="../templates")

CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")
if not CURRENCY_API_KEY:
    logger.error(
        "CURRENCY_API_KEY is not set. Check .env file or environment configuration."
    )

# Cache w pamięci (lazy loading)
_CURRENCY_NAMES_CACHE = {}
_CURRENCY_NAMES_LOADED = False


def get_currency_names():
    """Lazy loader nazw walut z cache w pamięci."""
    global _CURRENCY_NAMES_CACHE, _CURRENCY_NAMES_LOADED

    if _CURRENCY_NAMES_LOADED or not CURRENCY_API_KEY:
        return _CURRENCY_NAMES_CACHE

    try:
        timeout = current_app.config.get("REQUESTS_TIMEOUT", (5, 10))
        codes_url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/codes"
        response = requests.get(codes_url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success" and "supported_codes" in data:
            _CURRENCY_NAMES_CACHE = {
                code: name for code, name in data["supported_codes"]
            }
            _CURRENCY_NAMES_LOADED = True
            logger.info("Successfully loaded currency names from API.")
        else:
            logger.warning("Unexpected currency API response: %s", data)
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching currency codes: %s", e)
    except Exception:
        logger.exception("General error in loading currency names")

    return _CURRENCY_NAMES_CACHE


@currency_bp.route("/currency", methods=["GET", "POST"])
@login_required
def currency_converter():
    converted_amount = None
    currencies = []
    currency_logs = []
    favorite_currency_pairs = []
    timeout = current_app.config.get("REQUESTS_TIMEOUT", (5, 10))

    from_currency_selected = None
    to_currency_selected = None
    amount_entered = None

    if current_user.is_authenticated:
        favorite_currency_pairs = FavoriteCurrencyPair.query.filter_by(
            user_id=current_user.id
        ).all()

    try:
        symbols_url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(symbols_url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        currencies = sorted(data["rates"].keys())
    except requests.exceptions.RequestException as e:
        flash(f"Failed to load currency list: {e}.", "danger")
        logger.error("Error fetching currency symbols for dropdown: %s", e)

    if request.method == "POST":
        from_currency_form = request.form.get("from_currency")
        to_currency_form = request.form.get("to_currency")
        amount_str_form = request.form.get("amount")

        from_currency_selected = from_currency_form
        to_currency_selected = to_currency_form
        amount_entered = amount_str_form

        try:
            amount = float(amount_str_form)
            if amount <= 0:
                raise ValueError("The amount must be positive.")

            if not from_currency_form or not to_currency_form:
                flash("Please select both currencies and enter an amount.", "danger")
            else:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency_form}"
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.json()

                if to_currency_form in data["rates"]:
                    exchange_rate = data["rates"][to_currency_form]
                    converted_amount = amount * exchange_rate

                    if current_user.is_authenticated:
                        new_log = CurrencyLog(
                            user_id=current_user.id,
                            from_currency=from_currency_form,
                            to_currency=to_currency_form,
                            amount=amount,
                            converted_amount=converted_amount,
                            rate=exchange_rate,
                        )
                        db.session.add(new_log)
                        db.session.commit()
                        flash(
                            f"{amount:.2f} {from_currency_form} is {converted_amount:.2f} {to_currency_form}",
                            "success",
                        )
                else:
                    flash("Invalid target currency.", "danger")
        except (ValueError, TypeError):
            flash("Invalid amount. Please enter a positive number.", "danger")
        except requests.exceptions.RequestException as e:
            flash(f"Currency API connection error: {e}.", "danger")
            logger.error("Error fetching exchange rate: %s", e)
        except Exception as e:
            flash(f"An error occurred while converting: {e}", "danger")
            logger.exception("General error in currency conversion")

    elif request.method == "GET":
        from_currency_selected = request.args.get("from_currency")
        to_currency_selected = request.args.get("to_currency")
        amount_entered = request.args.get("amount")

    if current_user.is_authenticated:
        currency_logs = (
            CurrencyLog.query.filter_by(user_id=current_user.id)
            .order_by(CurrencyLog.timestamp.desc())
            .limit(10)
            .all()
        )

    return render_template(
        "currency.html",
        converted_amount=converted_amount,
        currencies=currencies,
        currency_logs=currency_logs,
        from_currency=from_currency_selected,
        to_currency=to_currency_selected,
        amount=amount_entered,
        favorite_currency_pairs=favorite_currency_pairs,
        currency_names=get_currency_names(),
    )


@currency_bp.route("/currency/add_favorite_pair", methods=["POST"])
@login_required
def add_favorite_pair():
    from_curr = request.form.get("from_currency")
    to_curr = request.form.get("to_currency")

    if not from_curr or not to_curr:
        flash(
            "Both 'From' and 'To' currencies are required to add a favorite pair.",
            "danger",
        )
        return redirect(url_for("currency.currency_converter"))

    existing_favorite = FavoriteCurrencyPair.query.filter_by(
        user_id=current_user.id, from_currency=from_curr, to_currency=to_curr
    ).first()

    if existing_favorite:
        flash(f"'{from_curr} to {to_curr}' is already in your favorite pairs!", "info")
    else:
        try:
            new_favorite_pair = FavoriteCurrencyPair(
                user_id=current_user.id, from_currency=from_curr, to_currency=to_curr
            )
            db.session.add(new_favorite_pair)
            db.session.commit()
            flash(f"'{from_curr} to {to_curr}' added to favorite pairs!", "success")
        except Exception as e:
            logger.exception("Error adding favorite currency pair")
            flash(f"Error adding favorite pair: {e}", "danger")
            db.session.rollback()

    return redirect(
        url_for(
            "currency.currency_converter", from_currency=from_curr, to_currency=to_curr
        )
    )


@currency_bp.route("/currency/remove_favorite_pair/<int:pair_id>", methods=["POST"])
@login_required
def remove_favorite_pair(pair_id):
    favorite_pair = db.get_or_404(FavoriteCurrencyPair, pair_id)

    if favorite_pair.user_id != current_user.id:
        flash("You are not authorized to remove this favorite pair.", "danger")
        return redirect(url_for("currency.currency_converter"))

    try:
        db.session.delete(favorite_pair)
        db.session.commit()
        flash(
            f"'{favorite_pair.from_currency} to {favorite_pair.to_currency}' removed from favorite pairs!",
            "success",
        )
    except Exception as e:
        logger.exception("Error removing favorite pair")
        flash(f"Error removing favorite pair: {e}", "danger")
        db.session.rollback()

    return redirect(url_for("currency.currency_converter"))
