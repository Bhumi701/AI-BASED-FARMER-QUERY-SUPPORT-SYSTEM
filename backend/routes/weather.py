from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.weather_service import weather_service

weather_bp = Blueprint("weather", __name__)


def _get_location_args():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if lat is not None and lon is not None:
        return None, float(lat), float(lon)
    return city, None, None


@weather_bp.route("/current", methods=["GET"])
@jwt_required()
def current():
    try:
        city, lat, lon = _get_location_args()
        if not city and lat is None:
            city = "Delhi"  # sensible default
        weather = weather_service.get_current(city=city, lat=lat, lon=lon)
        return jsonify({"success": True, "weather": weather})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@weather_bp.route("/forecast", methods=["GET"])
@jwt_required()
def forecast():
    try:
        city, lat, lon = _get_location_args()
        if not city and lat is None:
            city = "Delhi"
        forecast_data = weather_service.get_forecast(city=city, lat=lat, lon=lon, hours=24)
        return jsonify({"success": True, "forecast": forecast_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
