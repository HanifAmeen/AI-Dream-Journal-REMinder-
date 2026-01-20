from intents import PageMode
from decision_logic import should_ask_question
from choose_followup_questions import choose_followup_question
from followup_memory import FollowUpMemory
from reflection_builder import build_reflection
from local_llm import generate_reply
from conversation_memory import ConversationMemory


class ChatbotEngine:
    SYSTEM_PROMPT = """
You are REMinder, a calm dream companion.

STRICT RULES:
- Never explain your reasoning.
- Never describe what you are doing.
- Never mention page modes, system behavior, or conversation structure.
- Never say phrases like "In this response", "The assistant", or "This aligns with".
- Speak directly to the user as a human would.

STYLE:
- Be concise: 1–3 short paragraphs maximum.
- Prefer 2–4 sentences.
- No lectures. No analysis about analysis.
- If the user greets you, reply briefly and invite them to share a dream.
"""


    def __init__(self):
        self.memory = FollowUpMemory()
        self.conversation_memory = ConversationMemory()

    # ------------------------------
    # Main entry point
    # ------------------------------
    def respond(self, page, user_message=None, dream_context=None):
        if page == PageMode.HOME:
            return self._home(user_message)

        if page == PageMode.INPUT:
            return self._input()

        if page == PageMode.ANALYSIS:
            return self._analysis(dream_context)

        return self._llm_fallback(page, user_message, dream_context)

    # ------------------------------
    # LLM-powered fallback
    # ------------------------------
    def _llm_fallback(self, page, user_message=None, dream_context=None):
        if user_message:
            self.conversation_memory.add_user(user_message)

        context_block = ""
        if dream_context:
            context_block += f"\nDream context:\n{dream_context}"

        full_prompt = f"""
Conversation so far:
{self.conversation_memory.render()}

{context_block}

User message:
{user_message}
"""


        reply = generate_reply(self.SYSTEM_PROMPT, full_prompt)
        self.conversation_memory.add_bot(reply)

        return {
            "type": "answer",
            "response": reply
        }

    # ------------------------------
    # Page-specific handlers
    # ------------------------------
    def _home(self, user_message):
        return self._llm_fallback(
            page=PageMode.HOME,
            user_message=user_message
        )

    def _input(self):
        return self._llm_fallback(
            page=PageMode.INPUT,
            user_message="The user is preparing to describe a dream."
        )

    def _analysis(self, dream_context):
        dream_text = dream_context["dream_text"]
        symbols = dream_context["symbols"]
        dominant_emotion = dream_context["dominant_emotion"]

        if should_ask_question(dream_text, symbols, dominant_emotion):
            return {
                "type": "question",
                "response": choose_followup_question(symbols)
            }

        return self._llm_fallback(
            page=PageMode.ANALYSIS,
            user_message="Offer an insight about this dream.",
            dream_context=dream_context
        )

    # ------------------------------
    # Follow-up answer handler
    # ------------------------------
    def handle_followup_answer(self, dream_id, question, answer, dream_context):
        self.memory.store(dream_id, question, answer)

        reflection = build_reflection(
            dream_context,
            self.memory.get(dream_id)
        )

        return {
            "type": "reflection",
            "response": reflection
        }
