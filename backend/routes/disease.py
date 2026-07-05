import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import DiseaseDetectionHistory
from services.disease_service import disease_service

disease_bp = Blueprint("disease", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@disease_bp.route("/detect", methods=["POST"])
@jwt_required()
def detect():
    if not disease_service.is_ready():
        return jsonify({
            "success": False,
            "message": "Disease detection model not trained yet. "
                       "See backend/ml/disease_detection/README.md",
        }), 503

    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image uploaded."}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"success": False, "message": "No image selected."}), 400

    if not _allowed_file(image.filename):
        return jsonify({"success": False, "message": "Unsupported file type."}), 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    image.save(save_path)

    try:
        result = disease_service.predict(save_path)
    except Exception as e:
        return jsonify({"success": False, "message": f"Detection failed: {e}"}), 500

    user_id = int(get_jwt_identity())
    history = DiseaseDetectionHistory(
        user_id=user_id,
        crop=data_crop_or(request.form.get("crop_name"), result["crop"]),
        disease=result["disease"],
        confidence=result["confidence"],
        image_path=filename,
        recommendation=result["treatment"],
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        "success": True,
        "disease": result["disease"],
        "confidence": result["confidence"],
        "symptoms": result["symptoms"],
        "treatment": result["treatment"],
        "prevention": result["prevention"],
    })


def data_crop_or(user_supplied, predicted):
    return user_supplied if user_supplied and user_supplied != "Other" else predicted


@disease_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    records = (DiseaseDetectionHistory.query
               .filter_by(user_id=user_id)
               .order_by(DiseaseDetectionHistory.date.desc())
               .limit(20)
               .all())
    return jsonify({"success": True, "history": [r.to_dict() for r in records]})
