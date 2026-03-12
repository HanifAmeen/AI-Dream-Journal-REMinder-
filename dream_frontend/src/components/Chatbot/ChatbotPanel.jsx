import { useState, useEffect, useRef } from "react";
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
  const [conversationId, setConversationId] = useState(
    localStorage.getItem("conversation_id")
  );
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Fix 2: Create new conversation if none exists
  useEffect(() => {
    if (!conversationId) {
      fetch("http://127.0.0.1:5000/chatbot/new_chat", {
        method: "POST"
      })
        .then(res => res.json())
        .then(data => {
          setConversationId(data.conversation_id);
          localStorage.setItem("conversation_id", data.conversation_id);
        })
        .catch(err => console.error("Failed to create new chat:", err));
    }
  }, []);

  // Fix 4: Load chat history when conversationId is available
  useEffect(() => {
    if (!conversationId) return;

    fetch(`http://127.0.0.1:5000/chatbot/history/${conversationId}`)
      .then(res => res.json())
      .then(data => {
        if (data.messages) {
          setMessages(
            data.messages.map(m => ({
              role: m.role === "assistant" ? "bot" : "user",
              text: m.content
            }))
          );
        }
      })
      .catch(err => console.error("Failed to load chat history:", err));
  }, [conversationId]);

  // New Chat with confirmation
  const confirmNewChat = async () => {
    setShowConfirmDialog(false);
    try {
      const res = await fetch("http://127.0.0.1:5000/chatbot/new_chat", {
        method: "POST"
      });
      const data = await res.json();

      setConversationId(data.conversation_id);
      localStorage.setItem("conversation_id", data.conversation_id);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create new chat:", err);
    }
  };

  const newChat = () => {
    setShowConfirmDialog(true);
  };

  const sendMessage = async () => {
    if (!input.trim() || isTyping || !conversationId) return;

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
        dream_context: dreamContext,
        conversation_id: conversationId
      };
      setPendingQuestion(null);
    } else {
      body = {
        message: userInput,
        dream_context: dreamContext,
        conversation_id: conversationId
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

  if (!isOpen) return null;

  return (
    <>
      <div className="chatbot-panel">
        <div className="chatbot-header">
          <span>Spectors Corner</span>
          <div className="header-actions">
            <button 
              onClick={scrollToBottom}
              className="scroll-bottom-btn"
              title="Scroll to bottom"
            >
              ↓
            </button>
            <button onClick={newChat} className="new-chat-btn">
              New Chat
            </button>
          </div>
        </div>

        <div className="chatbot-messages" ref={messagesContainerRef}>
          {messages.map((m, i) => (
            <div
              key={i}
              className={`chatbot-message-row ${m.role}`}
            >
              {m.role === "bot" && (
                <Mascot state="replying" small />
              )}

              <div 
                className={`chatbot-message-bubble ${m.role}`}
                dangerouslySetInnerHTML={{ __html: m.text }}
              />
            </div>
          ))}

          {isTyping && (
            <div className="chatbot-message-row bot">
              <Mascot state="thinking" small />

              <div className="chatbot-message-bubble bot typing">
                Spector is thinking
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about your dream…"
            disabled={isTyping || !conversationId}
          />
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="confirm-dialog-overlay">
          <div className="confirm-dialog">
            <div className="confirm-dialog-content">
              <h3>Start New Chat?</h3>
              <p>This will clear your current conversation.</p>
              <div className="confirm-buttons">
                <button 
                  onClick={confirmNewChat}
                  className="confirm-yes-btn"
                >
                  Yes, New Chat
                </button>
                <button 
                  onClick={() => setShowConfirmDialog(false)}
                  className="confirm-no-btn"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
