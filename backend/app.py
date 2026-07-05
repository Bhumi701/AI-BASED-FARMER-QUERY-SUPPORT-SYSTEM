import os
from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from routes.auth import auth_bp
    from routes.crop import crop_bp
    from routes.disease import disease_bp
    from routes.chat import chat_bp
    from routes.weather import weather_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(crop_bp, url_prefix="/api/crop")
    app.register_blueprint(disease_bp, url_prefix="/api/disease")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")

    with app.app_context():
        db.create_all()

    from services.crop_service import init_crop_service
    from services.disease_service import init_disease_service
    from services.chat_service import init_chat_service
    from services.weather_service import init_weather_service

    init_crop_service(app)
    init_disease_service(app)
    init_chat_service(app)
    init_weather_service(app)

    @app.route("/api/health", methods=["GET"])
    def health():
        from services.crop_service import crop_service
        from services.disease_service import disease_service
        return jsonify({
            "status": "ok",
            "crop_model_ready": crop_service.is_ready(),
            "disease_model_ready": disease_service.is_ready(),
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Endpoint not found."}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"success": False, "message": "File too large."}), 413

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
