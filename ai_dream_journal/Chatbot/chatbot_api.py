from flask import Blueprint, request, jsonify
from chatbot_engine import ChatbotEngine
from intents import PageMode

chatbot_bp = Blueprint("chatbot", __name__)
bot = ChatbotEngine()


def parse_page_mode(page_str):
    try:
        return PageMode(page_str)
    except Exception:
        return PageMode.HOME


@chatbot_bp.route("/chatbot/respond", methods=["POST"])
def chatbot_respond():
    data = request.get_json(force=True)

    page = parse_page_mode(data.get("page", "home"))
    user_message = data.get("message")
    dream_context = data.get("dream_context")

    response = bot.respond(
        page=page,
        user_message=user_message,
        dream_context=dream_context
    )

    return jsonify(response)


@chatbot_bp.route("/chatbot/followup", methods=["POST"])
def chatbot_followup():
    data = request.get_json(force=True)

    response = bot.handle_followup_answer(
        dream_id=data["dream_id"],
        question=data["question"],
        answer=data["answer"],
        dream_context=data["dream_context"]
    )

    return jsonify(response)
