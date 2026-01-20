from chatbot_engine import ChatbotEngine
from intents import PageMode

bot = ChatbotEngine()

print(bot.respond(
    page=PageMode.HOME,
    user_message="Why do I keep dreaming about falling?"
))

print(bot.respond(
    page=PageMode.INPUT,
    dream_context={
        "dream_text": "I was running through a dark hallway and couldn’t escape."
    }
))

print(bot.respond(
    page=PageMode.ANALYSIS,
    dream_context={
        "dream_text": "I was late for an exam and everyone was watching.",
        "symbols": ["lateness", "exposure", "authority"],
        "dominant_emotion": "anxiety"
    }
))

print(bot.handle_followup_answer(
    dream_id=1,
    question="Is there something in waking life you feel unprepared for?",
    answer="Yes, I have an exam coming up and I feel behind.",
    dream_context={
        "dream_text": "I was late for an exam and everyone was watching.",
        "symbols": ["lateness", "exposure", "authority"],
        "dominant_emotion": "anxiety"
    }
))

