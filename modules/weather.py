from flask import Blueprint, render_template, request, request, flash, redirect, url_for
import requests
import os
from datetime import datetime
from flask_login import login_required, current_user
from extensions import db
from models import FavoriteWeatherLocation

weather_bp = Blueprint("weather", __name__, template_folder="../templates")

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    print(
        "ERROR: NO OPENWEATHER_API_KEY VARIABLE. Check .env file or environment configuration."
    )


def get_weather_data(city):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en"

    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        data = response.json()

        if data["cod"] != "200":
            return None, f"API Error: {data.get('message', 'Unknown error for {city}')}"

        display_city = data["city"]["name"]

        first_forecast = data["list"][0]
        current_weather_data = {
            "city": display_city,
            "temperature": first_forecast["main"]["temp"],
            "description": first_forecast["weather"][0]["description"].capitalize(),
            "icon": first_forecast["weather"][0]["icon"],
            "humidity": first_forecast["main"]["humidity"],
            "wind_speed": first_forecast["wind"]["speed"],
            "feels_like": first_forecast["main"]["feels_like"],
        }

        today = datetime.now().date()
        today_hourly_forecast = []
        upcoming_daily_forecast_grouped = []
        all_forecasts_by_day = {}

        for forecast_item in data["list"]:
            dt_object = datetime.fromtimestamp(forecast_item["dt"])
            forecast_date = dt_object.date()
            date_key = dt_object.strftime("%Y-%m-%d")

            if forecast_date == today:
                today_hourly_forecast.append(
                    {
                        "time": dt_object.strftime("%H:%M"),
                        "temp": forecast_item["main"]["temp"],
                        "icon": forecast_item["weather"][0]["icon"],
                        "description": forecast_item["weather"][0]["description"],
                    }
                )

            if date_key not in all_forecasts_by_day:
                all_forecasts_by_day[date_key] = []
            all_forecasts_by_day[date_key].append(forecast_item)

        for date_key in sorted(all_forecasts_by_day.keys()):
            day_dt_object = datetime.fromisoformat(date_key).date()

            if day_dt_object > today:
                day_forecast_items = all_forecasts_by_day[date_key]
                temps = [item["main"]["temp"] for item in day_forecast_items]
                min_temp = min(temps) if temps else None
                max_temp = max(temps) if temps else None

                representative_forecast = None
                for item in day_forecast_items:
                    if (
                        datetime.fromtimestamp(item["dt"]).hour >= 12
                        and datetime.fromtimestamp(item["dt"]).hour < 15
                    ):
                        representative_forecast = item
                        break
                if not representative_forecast and day_forecast_items:
                    representative_forecast = day_forecast_items[0]

                if representative_forecast:
                    hourly_details_for_day = []
                    for hr_item in day_forecast_items:
                        hr_dt_object = datetime.fromtimestamp(hr_item["dt"])
                        hourly_details_for_day.append(
                            {
                                "time": hr_dt_object.strftime("%H:%M"),
                                "temp": hr_item["main"]["temp"],
                                "icon": hr_item["weather"][0]["icon"],
                                "description": hr_item["weather"][0]["description"],
                            }
                        )

                    upcoming_daily_forecast_grouped.append(
                        {
                            "date": date_key,
                            "day_name": datetime.fromisoformat(date_key).strftime("%A"),
                            "min_temp": min_temp,
                            "max_temp": max_temp,
                            "icon": representative_forecast["weather"][0]["icon"],
                            "description": representative_forecast["weather"][0][
                                "description"
                            ].capitalize(),
                            "hourly_details": hourly_details_for_day,
                        }
                    )
        return {
            "current_weather_data": current_weather_data,
            "today_hourly_forecast": today_hourly_forecast,
            "upcoming_daily_forecast_grouped": upcoming_daily_forecast_grouped,
        }, None

    except requests.exceptions.RequestException as e:
        return None, f"API connection error: {e}. Check city name or API key."
    except KeyError as e:
        return (
            None,
            f"API data structure error: Missing key {e}. Please try again or contact administrator.",
        )
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"


@weather_bp.route("/weather", methods=["GET", "POST"])
def weather():
    current_weather_data = None
    today_hourly_forecast = []
    upcoming_daily_forecast_grouped = []
    error = None
    city_to_display = None

    favorite_locations = []
    if current_user.is_authenticated:
        favorite_locations = FavoriteWeatherLocation.query.filter_by(
            user_id=current_user.id
        ).all()

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            city_to_display = city
        else:
            error = "Please enter a city name."
    elif request.args.get("city"):
        city_to_display = request.args.get("city")
    elif current_user.is_authenticated and favorite_locations:
        city_to_display = favorite_locations[0].city_name

    if city_to_display:
        weather_results, weather_error = get_weather_data(city_to_display)
        if weather_results:
            current_weather_data = weather_results["current_weather_data"]
            today_hourly_forecast = weather_results["today_hourly_forecast"]
            upcoming_daily_forecast_grouped = weather_results[
                "upcoming_daily_forecast_grouped"
            ]
        else:
            error = weather_error

    return render_template(
        "weather.html",
        current_weather_data=current_weather_data,
        today_hourly_forecast=today_hourly_forecast,
        upcoming_daily_forecast_grouped=upcoming_daily_forecast_grouped,
        error=error,
        favorite_locations=favorite_locations,
        displayed_city=city_to_display,
    )


@weather_bp.route("/weather/add_favorite/<city_name>", methods=["POST"])
@login_required
def add_favorite_weather(city_name):
    existing_favorite = FavoriteWeatherLocation.query.filter_by(
        user_id=current_user.id, city_name=city_name
    ).first()

    if existing_favorite:
        flash(f"'{city_name}' is already in your favorites!", "info")
    else:
        try:
            new_favorite = FavoriteWeatherLocation(
                user_id=current_user.id, city_name=city_name
            )
            db.session.add(new_favorite)
            db.session.commit()
            flash(f"'{city_name}' added to favorites!", "success")
        except Exception as e:
            flash(f"Error adding '{city_name}' to favorites: {e}", "danger")
            db.session.rollback()

    return redirect(url_for("weather.weather", city=city_name))


@weather_bp.route("/weather/remove_favorite/<int:location_id>", methods=["POST"])
@login_required
def remove_favorite_weather(location_id):
    favorite_location = FavoriteWeatherLocation.query.get_or_404(location_id)

    if favorite_location.user_id != current_user.id:
        flash("You are not authorized to remove this favorite location.", "danger")
        return redirect(url_for("weather.weather"))

    try:
        db.session.delete(favorite_location)
        db.session.commit()
        flash(f"'{favorite_location.city_name}' removed from favorites!", "success")
    except Exception as e:
        flash(f"Error removing favorite location: {e}", "danger")
        db.session.rollback()

    return redirect(url_for("weather.weather"))
