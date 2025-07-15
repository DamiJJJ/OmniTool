import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

OPENWEATHER_API_KEY = "c58789670bdbb47b3015c68589ed18e3" #os.environ.get("OPENWEATHER_API_KEY")

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
                error = "Could not download weather forecast data. Check the city name."
        else:
            error = "Please provide city name."
    return render_template('weather.html', weather_data=weather_data, error=error)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)