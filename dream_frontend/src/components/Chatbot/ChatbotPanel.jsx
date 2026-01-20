import { useState } from "react";
import { useChatbot } from "../../context/ChatbotContext";
import "./chatbot.css";
import Mascot from "./Mascot";


export default function ChatbotPanel({ page, dreamContext }) {
  const {
    isOpen,
    messages,
    setMessages,
    pendingQuestion,
    setPendingQuestion,
    isTyping,
    setIsTyping
  } = useChatbot();

  const [input, setInput] = useState("");

  if (!isOpen) return null;

 const sendMessage = async () => {
  if (!input.trim() || isTyping) return;

  const userInput = input;

  // 1️⃣ Show user message immediately
  setMessages((prev) => [...prev, { role: "user", text: userInput }]);
  setInput("");

  // 2️⃣ Enter thinking state
  setIsTyping(true);

  let endpoint = "/chatbot/respond";
  let body = {};

  if (pendingQuestion) {
    endpoint = "/chatbot/followup";
    body = {
      dream_id: dreamContext?.id || 1,
      question: pendingQuestion,
      answer: userInput,
      dream_context: dreamContext
    };
    setPendingQuestion(null);
  } else {
    body = {
      page,
      message: userInput,
      dream_context: dreamContext
    };
  }

  const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await res.json();

  // 3️⃣ Artificial thinking delay (UX polish)
  setTimeout(() => {
    setIsTyping(false);

    setMessages((prev) => [
      ...prev,
      { role: "bot", text: data.response }
    ]);

    if (data.type === "question") {
      setPendingQuestion(data.response);
    }
  }, 3000);
};


  return (
 <div className="chatbot-panel">
  <div className="chatbot-header">REMinder Guide</div>

  <div className="chatbot-messages">
    {messages.map((m, i) => (
  <div
    key={i}
    className={`chatbot-message-row ${m.role}`}
  >
    {m.role === "bot" && (
      <Mascot state="replying" small />
    )}

    <div className={`chatbot-message-bubble ${m.role}`}>
      {m.text}
    </div>
  </div>
))}


   {isTyping && (
  <div className="chatbot-message-row bot">
    <Mascot state="thinking" small />

    <div className="chatbot-message-bubble bot typing">
      REMinder is thinking
      <span className="dot">.</span>
      <span className="dot">.</span>
      <span className="dot">.</span>
    </div>
  </div>
)}

  </div>



  <div className="chatbot-input">
    <input
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      placeholder="Ask about your dream…"
      disabled={isTyping}
    />
  </div>
</div>

  );
}
