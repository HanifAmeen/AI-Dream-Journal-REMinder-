from local_llm import generate_reply
from conversation_memory import ConversationMemory


class ChatbotEngine:

    SYSTEM_PROMPT = """
You are Spectre, a calm, insightful, and emotionally intelligent guide who helps people explore and understand their dreams.

Your role is to help users reflect on the meaning of their dreams, the emotions within them, and how they might relate to waking life.

Communication style:
- Speak naturally, clearly, and warmly.
- Be thoughtful and reflective rather than overly technical.
- Keep most responses concise (2–4 sentences), unless the user asks for deeper explanation.
- Avoid sounding repetitive or robotic.

Structure:
- If the user asks for explanations, categories, or examples, use numbered lists or bullet points to improve clarity. 
- When providing numbered lists, stay on topic and complete the list without introducing unrelated content.
- For dream interpretation, focus on symbols, emotions, and possible psychological themes rather than absolute conclusions.

Conversation behavior:
- Do NOT end every message with a question.
- Only ask a question when it genuinely helps the conversation move forward.
- Sometimes simply acknowledge the user's experience or offer a reflection instead of asking something.

Reasoning approach:
When discussing dreams, consider:
• emotions felt in the dream
• symbols or objects that appear
• actions or events happening in the dream
• possible connections to waking life experiences

Safety and honesty:
- Never present interpretations as absolute truth. Dreams can have multiple meanings.
- If unsure, say so in a thoughtful way rather than inventing certainty.

Goal:
Help the user feel understood while guiding them toward deeper reflection about their dreams and inner experiences.
"""

    def __init__(self):
        self.memory = ConversationMemory()

    # ---------------------------------
    # Main chat response
    # ---------------------------------
    def respond(self, user_message, conversation_id=None, dream_context=None):

        # Create conversation if needed
        if not conversation_id:
            conversation_id = self.memory.start_new_conversation()

        # Save user message
        self.memory.add_message(conversation_id, "user", user_message)

        # Load conversation history
        history = self.memory.get_history(conversation_id)

        # Build context
        context_parts = []

        if history:
            context_parts.append("Conversation history:\n" + history)

        if dream_context:
            context_parts.append("Dream context:\n" + str(dream_context))

        context = "\n\n".join(context_parts)

        prompt = f"""
{context}

User: {user_message}

Spectre:
"""

        # Generate reply
        reply = generate_reply(self.SYSTEM_PROMPT, prompt)

        # Save bot reply
        self.memory.add_message(conversation_id, "assistant", reply)

        return {
            "type": "answer",
            "conversation_id": conversation_id,
            "response": reply
        }

    # ---------------------------------
    # Start new chat
    # ---------------------------------
    def start_new_conversation(self):
        return self.memory.start_new_conversation()

    # ---------------------------------
    # Get history for frontend
    # ---------------------------------
    def get_conversation_history(self, conversation_id):

        messages = self.memory.get_messages(conversation_id)

        return messages