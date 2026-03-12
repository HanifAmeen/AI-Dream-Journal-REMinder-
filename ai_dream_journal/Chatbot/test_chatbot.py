from chatbot_engine import ChatbotEngine

bot = ChatbotEngine()

# start new conversation
conversation_id = bot.start_new_conversation()

print("Spectre chatbot test started\n")

while True:
    
    user_input = input("You: ")

    if user_input.lower() in ["quit", "exit"]:
        break

    response = bot.respond(
        user_message=user_input,
        conversation_id=conversation_id
    )

    print("Spectre:", response["response"])