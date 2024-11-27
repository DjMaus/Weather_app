from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API key from environment variables
API_KEY = os.getenv("API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')  # Get 'city' parameter from the query string

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    # Step 2: Use Geocoding API to get latitude and longitude
    geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
    geocode_params = {
        "q": f"{city},FI",  # Assuming Finnish cities; adjust country code as needed
        "appid": API_KEY,
        "limit": 1
    }
    geocode_response = requests.get(geocode_url, params=geocode_params)

    if geocode_response.status_code != 200:
        return jsonify({"error": "Failed to fetch coordinates", "details": geocode_response.json()}), geocode_response.status_code

    geocode_data = geocode_response.json()
    if not geocode_data:
        return jsonify({"error": f"No coordinates found for city: {city}"}), 404

    # Extract latitude and longitude from geocode response
    lat = geocode_data[0]["lat"]
    lon = geocode_data[0]["lon"]

    # Step 3: Fetch weather data using coordinates
    weather_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    weather_response = requests.get(BASE_URL, params=weather_params)

    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        weather_info = {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "weather": weather_data["weather"][0]["description"].capitalize(),
            "wind_speed": weather_data["wind"]["speed"]
        }
        return jsonify(weather_info), 200
    else:
        return jsonify({"error": "Failed to fetch weather data", "details": weather_response.json()}), weather_response.status_code




if __name__ == '__main__':
    app.run(debug=True)
