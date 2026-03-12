from flask import Blueprint, request, jsonify
from chatbot_engine import ChatbotEngine

chatbot_bp = Blueprint("chatbot", __name__)

# Initialize chatbot engine once
bot = ChatbotEngine()


# ---------------------------------------
# Main Chat Endpoint
# ---------------------------------------
@chatbot_bp.route("/chatbot/respond", methods=["POST"])
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
        dream_context=dream_context
    )

    return jsonify(response)


# ---------------------------------------
# Start New Conversation
# ---------------------------------------
@chatbot_bp.route("/chatbot/new_chat", methods=["POST"])
def new_chat():

    conversation_id = bot.start_new_conversation()

    return jsonify({
        "conversation_id": conversation_id
    })


# ---------------------------------------
# Optional: Get Conversation History
# ---------------------------------------
@chatbot_bp.route("/chatbot/history/<conversation_id>", methods=["GET"])
def get_chat_history(conversation_id):

    history = bot.get_conversation_history(conversation_id)

    return jsonify({
        "conversation_id": conversation_id,
        "messages": history
    })