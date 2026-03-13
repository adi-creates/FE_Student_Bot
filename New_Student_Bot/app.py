import os
import random
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from kb_engine import KnowledgeBaseBot


BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "model.pkl"
DOCX_PATH = BASE_DIR / "TCET_FE_faq.docx"
CONFIDENCE_THRESHOLD = 0.2


app = Flask(__name__)
kb_bot = None


def ensure_model() -> KnowledgeBaseBot:
    global kb_bot

    if kb_bot is not None:
        return kb_bot

    if MODEL_PATH.exists():
        kb_bot = KnowledgeBaseBot.load(str(MODEL_PATH))
        return kb_bot

    if not DOCX_PATH.exists():
        raise FileNotFoundError(f"Source document missing: {DOCX_PATH}")

    kb_bot = KnowledgeBaseBot.train_from_docx(str(DOCX_PATH))
    kb_bot.save(str(ARTIFACT_DIR))
    return kb_bot


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    try:
        bot = ensure_model()
        return jsonify({"status": "ok", "faq_count": len(bot.faqs)})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/ask", methods=["POST"])
def ask():
    try:
        bot = ensure_model()
        payload = request.get_json(silent=True) or {}
        question = str(payload.get("question", "")).strip()

        if not question:
            return jsonify({"error": "Question is required."}), 400

        faq_item, confidence = bot.ask(question)
        if confidence < CONFIDENCE_THRESHOLD:
            return jsonify(
                {
                    "answer": "I could not find a confident answer in the TCET FE FAQ document. Please rephrase your question.",
                    "confidence": round(confidence, 4),
                    "source_question": faq_item.question,
                }
            )

        return jsonify(
            {
                "answer": faq_item.answer,
                "confidence": round(confidence, 4),
                "source_question": faq_item.question,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/suggestions")
def suggestions():
    try:
        bot = ensure_model()
        count = request.args.get("count", default=4, type=int)
        count = max(3, min(count, 4))

        questions = [faq.question for faq in bot.faqs if faq.question]
        if not questions:
            return jsonify({"questions": []})

        sample_size = min(count, len(questions))
        return jsonify({"questions": random.sample(questions, sample_size)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    ensure_model()
    app.run(host="0.0.0.0", port=port, debug=True)
