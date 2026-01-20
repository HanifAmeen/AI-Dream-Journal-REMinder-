import { useChatbot } from "../../context/ChatbotContext";
import "./chatbot.css";

export default function ChatbotButton() {
  const { toggleChat } = useChatbot();

  return (
    <button
      className="chatbot-button"
      onClick={toggleChat}
      aria-label="Open dream guide"
    >
      💭
    </button>
  );
}
