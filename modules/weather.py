from flask import Blueprint, render_template, request
import requests
import os

weather_bp = Blueprint('weather', __name__, template_folder='../templates')

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY") 
if not OPENWEATHER_API_KEY:
    print("ERROR: NO OPENWEATHER_API_KEY VARIABLE. Check .env file or environment configuration.")

@weather_bp.route('/weather', methods=['GET', 'POST'])
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