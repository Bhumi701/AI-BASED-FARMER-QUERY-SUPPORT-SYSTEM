from flask import Blueprint, request, jsonify
from extensions import db
from models import ChatHistory
from services.chat_service import chat_service

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    lang = data.get("lang", "en")
    user_id_raw = data.get("user_id", "anonymous")

    if not message:
        return jsonify({"status": "error", "error": "Message cannot be empty."}), 400

    try:
        reply = chat_service.get_reply(message, lang=lang)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

    # Save history only if we have a real logged-in numeric user id
    try:
        user_id = int(user_id_raw)
        history = ChatHistory(user_id=user_id, message=message, reply=reply)
        db.session.add(history)
        db.session.commit()
    except (ValueError, TypeError):
        pass  # anonymous user, skip saving

    return jsonify({"status": "success", "reply": reply})
