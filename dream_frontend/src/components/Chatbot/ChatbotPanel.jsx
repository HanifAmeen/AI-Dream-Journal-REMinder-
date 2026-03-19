import { useState, useEffect, useRef } from "react";
import { useChatbot } from "../../context/ChatbotContext";
import "./chatbot.css";
import Mascot from "./Mascot";

// ✅ OPTIONAL BUT CLEAN: define headers once
const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
});

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

  // ✅ NEW: Cancel request function
  const cancelRequest = () => {
    setIsTyping(false);
  };

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // ✅ STEP 3 — FIXED HISTORY LOADER (with auth header)
  useEffect(() => {
    const loadChat = async () => {
      const storedId = localStorage.getItem("conversation_id");
      if (!storedId) return;

      try {
        const res = await fetch(
          `http://127.0.0.1:5000/chatbot/history/${storedId}`,
          {
            headers: getAuthHeaders()
          }
        );

        const data = await res.json();

        if (data.messages) {
          setConversationId(storedId);
          setMessages(
            data.messages.map(m => ({
              role: m.role === "assistant" ? "bot" : "user",
              text: m.content
            }))
          );
        }
      } catch (err) {
        console.error("Failed to load chat history:", err);
      }
    };

    loadChat();
  }, []);

  // ✅ STEP 3: KEEP newChat() as is (user explicitly wants new chat)
  const confirmNewChat = async () => {
    setShowConfirmDialog(false);
    try {
      const res = await fetch("http://127.0.0.1:5000/chatbot/new_chat", {
        method: "POST",
        headers: getAuthHeaders()
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

  // ✅ STEP 1 & STEP 2 — FIXED sendMessage() (with auth everywhere)
  const sendMessage = async () => {
    if (!input.trim() || isTyping) return;

    const userInput = input;

    // 1️⃣ Show user message immediately
    setMessages(prev => [...prev, { role: "user", text: userInput }]);
    setInput("");

    // 2️⃣ Enter thinking state
    setIsTyping(true);

    // ✅ STEP 2 — Create conversation if needed (with auth)
    let currentId = conversationId;
    if (!currentId) {
      const res = await fetch("http://127.0.0.1:5000/chatbot/new_chat", {
        method: "POST",
        headers: getAuthHeaders()
      });

      const data = await res.json();
      currentId = data.conversation_id;
      setConversationId(currentId);
      localStorage.setItem("conversation_id", currentId);
    }

    let endpoint = "/chatbot/respond";
    let body = {};

    if (pendingQuestion) {
      endpoint = "/chatbot/followup";
      body = {
        dream_id: dreamContext?.id || 1,
        question: pendingQuestion,
        answer: userInput,
        conversation_id: currentId,
        dream_context: dreamContext
      };
      setPendingQuestion(null);
    } else {
      // ✅ STEP 1 — Fixed body with conversation_id
      body = {
        message: userInput,
        conversation_id: currentId,
        dream_context: dreamContext
      };
    }

    const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
    });

    const data = await res.json();

    // 3️⃣ Artificial thinking delay (UX polish)
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [
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

              {/* ✅ UPDATED: Typing indicator with Cancel button */}
              <div className="chatbot-message-bubble bot typing">
                Spector is thinking
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>

                <button
                  className="cancel-btn"
                  onClick={cancelRequest}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ✅ UPDATED: Input with Send button */}
        <div className="chatbot-input">
          <textarea
            className="chatbot-textarea"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask about your dream…"
            disabled={isTyping}
          />

          <button
            className="chatbot-send-btn"
            onClick={sendMessage}
            disabled={isTyping || !input.trim()}
          >
            Send
          </button>
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
