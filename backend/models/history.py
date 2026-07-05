from datetime import datetime
from extensions import db


class CropRecommendationHistory(db.Model):
    __tablename__ = "crop_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    nitrogen = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    ph = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    season = db.Column(db.String(20))

    crop = db.Column(db.String(80))
    confidence = db.Column(db.Float)
    top_matches = db.Column(db.JSON)

    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "crop": self.crop,
            "confidence": self.confidence,
            "top_matches": self.top_matches,
            "date": self.date.isoformat(),
        }


class DiseaseDetectionHistory(db.Model):
    __tablename__ = "disease_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    crop = db.Column(db.String(80))
    disease = db.Column(db.String(120))
    confidence = db.Column(db.Float)
    image_path = db.Column(db.String(255))
    recommendation = db.Column(db.Text)

    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "crop": self.crop,
            "disease": self.disease,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "date": self.date.isoformat(),
        }


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
