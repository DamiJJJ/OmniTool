from flask import Blueprint, render_template, request
import requests
import os
from datetime import datetime, timedelta

weather_bp = Blueprint('weather', __name__, template_folder='../templates')

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY") 
if not OPENWEATHER_API_KEY:
    print("ERROR: NO OPENWEATHER_API_KEY VARIABLE. Check .env file or environment configuration.")

@weather_bp.route('/weather', methods=['GET', 'POST'])
def weather():
    current_weather_data = None
    today_hourly_forecast = []
    upcoming_daily_forecast_grouped = []
    error = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en" 
            
            try:
                response = requests.get(forecast_url)
                response.raise_for_status()
                data = response.json()

                if data['cod'] != '200':
                    error = f"API Error: {data.get('message', 'Unknown error')}"
                    return render_template('weather.html', current_weather_data=current_weather_data, error=error, today_hourly_forecast=today_hourly_forecast, upcoming_daily_forecast=upcoming_daily_forecast)

                display_city = data['city']['name']

                first_forecast = data['list'][0]
                current_weather_data = {
                    'city': display_city,
                    'temperature': first_forecast['main']['temp'],
                    'description': first_forecast['weather'][0]['description'].capitalize(),
                    'icon': first_forecast['weather'][0]['icon'],
                    'humidity': first_forecast['main']['humidity'],
                    'wind_speed': first_forecast['wind']['speed'],
                    'feels_like': first_forecast['main']['feels_like']
                }

                today = datetime.now().date()
                
                all_forecasts_by_day = {}

                for forecast_item in data['list']:
                    dt_object = datetime.fromtimestamp(forecast_item['dt'])
                    forecast_date = dt_object.date()
                    date_key = dt_object.strftime('%Y-%m-%d')

                    if forecast_date == today:
                        today_hourly_forecast.append({
                            'time': dt_object.strftime('%H:%M'),
                            'temp': forecast_item['main']['temp'],
                            'icon': forecast_item['weather'][0]['icon'],
                            'description': forecast_item['weather'][0]['description']
                        })
                    
                    if date_key not in all_forecasts_by_day:
                        all_forecasts_by_day[date_key] = []
                    all_forecasts_by_day[date_key].append(forecast_item)
                    
                for date_key in sorted(all_forecasts_by_day.keys()):
                    day_dt_object = datetime.fromisoformat(date_key).date()

                    if day_dt_object > today:
                        day_forecast_items = all_forecasts_by_day[date_key]
                        
                        # Calculate min/max temp for the day
                        temps = [item['main']['temp'] for item in day_forecast_items]
                        min_temp = min(temps) if temps else None
                        max_temp = max(temps) if temps else None

                        representative_forecast = None
                        for item in day_forecast_items:
                            if datetime.fromtimestamp(item['dt']).hour >= 12 and datetime.fromtimestamp(item['dt']).hour < 15:
                                representative_forecast = item
                                break
                        if not representative_forecast and day_forecast_items: # Fallback to first if no midday entry
                            representative_forecast = day_forecast_items[0]

                        if representative_forecast:
                            # Prepare hourly details for this specific day
                            hourly_details_for_day = []
                            for hr_item in day_forecast_items:
                                hr_dt_object = datetime.fromtimestamp(hr_item['dt'])
                                hourly_details_for_day.append({
                                    'time': hr_dt_object.strftime('%H:%M'),
                                    'temp': hr_item['main']['temp'],
                                    'icon': hr_item['weather'][0]['icon'],
                                    'description': hr_item['weather'][0]['description']
                                })

                            upcoming_daily_forecast_grouped.append({
                                'date': date_key,
                                'day_name': datetime.fromisoformat(date_key).strftime('%A'),
                                'min_temp': min_temp,
                                'max_temp': max_temp,
                                'icon': representative_forecast['weather'][0]['icon'],
                                'description': representative_forecast['weather'][0]['description'].capitalize(),
                                'hourly_details': hourly_details_for_day
                            })

            except requests.exceptions.RequestException as e:
                error = f"API connection error: {e}. Check city name or API key."
                print(f"Error fetching weather data for {city}: {e}")
            except KeyError as e:
                error = f"API data structure error: Missing key {e}. Please try again or contact administrator."
                print(f"KeyError in weather module: {e} in data: {data}")
            except Exception as e:
                error = f"An unexpected error occurred: {e}"
                print(f"General error in weather module for {city}: {e}")
        else:
            error = "Please enter a city name."
            
    return render_template('weather.html', 
                           current_weather_data=current_weather_data, 
                           today_hourly_forecast=today_hourly_forecast, 
                           upcoming_daily_forecast_grouped=upcoming_daily_forecast_grouped, 
                           error=error)
