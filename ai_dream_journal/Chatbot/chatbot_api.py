from flask import Blueprint, request, jsonify
from chatbot_engine import ChatbotEngine
from ai_dream_journal.auth_utils import auth_required


chatbot_bp = Blueprint("chatbot", __name__)


# Initialize chatbot engine once
bot = ChatbotEngine()


# ---------------------------------------
# Main Chat Endpoint
# ---------------------------------------
@chatbot_bp.route("/chatbot/respond", methods=["POST"])
@auth_required
def chatbot_respond():
    data = request.get_json(force=True)

    user_message = data.get("message")
    conversation_id = data.get("conversation_id")
    dream_context = data.get("dream_context")

    if not user_message:
        return jsonify({
            "error": "No message provided"
        }), 400

    response = bot.respond(
        user_message=user_message,
        conversation_id=conversation_id,
        dream_context=dream_context,
        user_id=request.user_id
    )

    return jsonify(response)


# ---------------------------------------
# Start New Conversation
# ---------------------------------------
@chatbot_bp.route("/chatbot/new_chat", methods=["POST"])
@auth_required
def new_chat():
    conversation_id = bot.start_new_conversation(request.user_id)

    return jsonify({
        "conversation_id": conversation_id
    })


# ---------------------------------------
# Optional: Get Conversation History
# ---------------------------------------
@chatbot_bp.route("/chatbot/history/<conversation_id>", methods=["GET"])
@auth_required
def get_chat_history(conversation_id):
    history = bot.get_conversation_history(conversation_id, request.user_id)

    return jsonify({
        "conversation_id": conversation_id,
        "messages": history
    })
