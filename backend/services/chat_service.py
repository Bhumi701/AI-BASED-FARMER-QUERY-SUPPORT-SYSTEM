import os
import json


class ChatService:
    def __init__(self):
        self.schemes = []
        self.client = None
        self._ready = False

    def load(self, schemes_path, api_key):
        if os.path.exists(schemes_path):
            with open(schemes_path) as f:
                self.schemes = json.load(f)

        if not api_key:
            print("[ChatService] GEMINI_API_KEY not set - chatbot will use fallback responses.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self._ready = True
            print("[ChatService] Gemini chatbot ready (new google-genai SDK, gemini-2.5-flash).")
        except Exception as e:
            print(f"[ChatService] Failed to init Gemini: {e}")

    def _relevant_schemes(self, message, max_schemes=3):
        message_lower = message.lower()
        message_words = set(w.strip(".,!?") for w in message_lower.split())
        scored = []
        for scheme in self.schemes:
            text = (scheme["name"] + " " + scheme["summary"] + " " + scheme["eligibility"]).lower()
            text_words = set(text.split())
            score = sum(1 for word in message_words if len(word) > 3 and word in text_words)
            if score > 0:
                scored.append((score, scheme))
        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            if any(k in message_lower for k in ["scheme", "yojana", "subsidy", "sarkar", "government", "policy"]):
                return self.schemes[:max_schemes]
            return []
        return [s for _, s in scored[:max_schemes]]

    def _build_prompt(self, message, lang, schemes):
        scheme_context = ""
        if schemes:
            scheme_context = "\n\nRelevant government schemes you can mention if useful:\n"
            for s in schemes:
                scheme_context += f"- {s['name']}: {s['summary']} (Eligibility: {s['eligibility']})\n"

        lang_instruction = {
            "hi": "Reply in simple Hindi.",
            "en": "Reply in simple English.",
        }.get(lang, "Reply in simple English, mixing Hindi words naturally if the farmer's question used Hindi.")

        return (
            "You are a helpful farming assistant for Indian farmers. Answer clearly and practically, "
            "keep it concise (under 150 words) and easy to understand for someone without technical background. "
            f"{lang_instruction}\n"
            f"{scheme_context}\n\n"
            f"Farmer's question: {message}"
        )

    def _fallback_reply(self, message, schemes):
        if schemes:
            lines = ["Here are some government schemes that might help:"]
            for s in schemes:
                lines.append(f"- {s['name']}: {s['summary']}")
            return "\n".join(lines)
        return (
            "I'm currently running in limited mode (Gemini API not reachable). "
            "Please try again in a moment, or ask specifically about government schemes."
        )

    def get_reply(self, message, lang="en"):
        schemes = self._relevant_schemes(message)

        if not self._ready or self.client is None:
            return self._fallback_reply(message, schemes)

        try:
            prompt = self._build_prompt(message, lang, schemes)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ChatService] Gemini error: {e}")
            return self._fallback_reply(message, schemes)


chat_service = ChatService()


def init_chat_service(app):
    with app.app_context():
        schemes_path = os.path.join(app.root_path, "data", "govt_schemes.json")
        chat_service.load(schemes_path, app.config["GEMINI_API_KEY"])