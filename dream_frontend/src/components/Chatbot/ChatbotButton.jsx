import { useChatbot } from "../../context/ChatbotContext";
import "./chatbot.css";

// import mascot avatar
import MKAvatar from "../../Assets/Mascot/MK_avatar.png";;

export default function ChatbotButton() {
  const { toggleChat } = useChatbot();

  return (
    <button
      className="chatbot-button"
      onClick={toggleChat}
      aria-label="Open dream guide"
    >
      <img 
        src={MKAvatar}
        alt="Dream Guide"
        className="chatbot-avatar"
      />
    </button>
  );
}