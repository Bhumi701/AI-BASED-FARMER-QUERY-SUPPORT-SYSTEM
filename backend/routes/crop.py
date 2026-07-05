from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import CropRecommendationHistory
from services.crop_service import crop_service

crop_bp = Blueprint("crop", __name__)


@crop_bp.route("/recommend", methods=["POST"])
@jwt_required()
def recommend():
    if not crop_service.is_ready():
        return jsonify({
            "success": False,
            "message": "Crop model not trained yet. Run ml/crop_recommendation/train_crop_model.py",
        }), 503

    data = request.get_json(force=True, silent=True) or {}
    required = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        rainfall = float(data["rainfall"])
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "All soil parameters must be numbers."}), 400

    recommendations = crop_service.predict(
        nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, top_k=3
    )

    user_id = int(get_jwt_identity())
    top = recommendations[0]
    history = CropRecommendationHistory(
        user_id=user_id,
        nitrogen=nitrogen, phosphorus=phosphorus, potassium=potassium,
        temperature=temperature, humidity=humidity, ph=ph, rainfall=rainfall,
        season=data.get("season"),
        crop=top["crop"], confidence=top["confidence"], top_matches=recommendations,
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        "success": True,
        "recommendations": recommendations,
        "soil_analysis": {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "ph": ph,
        },
    })


@crop_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    records = (CropRecommendationHistory.query
               .filter_by(user_id=user_id)
               .order_by(CropRecommendationHistory.date.desc())
               .limit(20)
               .all())
    return jsonify({"success": True, "history": [r.to_dict() for r in records]})
