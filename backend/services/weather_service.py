import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherService:
    def __init__(self):
        self.api_key = None

    def init_app(self, api_key):
        self.api_key = api_key

    def _location_params(self, city=None, lat=None, lon=None):
        if city:
            return {"q": city}
        if lat is not None and lon is not None:
            return {"lat": lat, "lon": lon}
        raise ValueError("Provide either city or lat/lon")

    def get_current(self, city=None, lat=None, lon=None, units="metric"):
        if not self.api_key:
            raise RuntimeError("OPENWEATHER_API_KEY not configured on the server.")

        params = self._location_params(city, lat, lon)
        params.update({"appid": self.api_key, "units": units})

        resp = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            "location": f"{data.get('name', 'Unknown')}, {data.get('sys', {}).get('country', '')}".strip(", "),
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "clouds": data.get("clouds", {}).get("all", 0),
            "description": data["weather"][0]["description"],
        }

    def get_forecast(self, city=None, lat=None, lon=None, units="metric", hours=24):
        if not self.api_key:
            raise RuntimeError("OPENWEATHER_API_KEY not configured on the server.")

        params = self._location_params(city, lat, lon)
        params.update({"appid": self.api_key, "units": units})

        resp = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # OpenWeatherMap free "forecast" endpoint returns 3-hour steps.
        # Grab enough steps to cover the requested window (default next 24h = 8 steps).
        steps_needed = max(1, hours // 3)
        forecast_list = []
        for item in data.get("list", [])[:steps_needed]:
            forecast_list.append({
                "time": item["dt_txt"],
                "temperature": round(item["main"]["temp"], 1),
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"],
                "humidity": item["main"]["humidity"],
            })
        return forecast_list


weather_service = WeatherService()


def init_weather_service(app):
    weather_service.init_app(app.config["OPENWEATHER_API_KEY"])
