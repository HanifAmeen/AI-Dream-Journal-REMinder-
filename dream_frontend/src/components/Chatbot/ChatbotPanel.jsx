import { useState, useEffect, useRef } from "react";
import { useChatbot } from "../../context/ChatbotContext";
import "./chatbot.css";
import Mascot from "./Mascot";

// ✅ Safe auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` })
  };
};

export default function ChatbotPanel({ page, dreamContext }) {
  const {
    isOpen,
    messages,
    setMessages,
    pendingQuestion,
    setPendingQuestion,
    isTyping,
    setIsTyping,
    setIsOpen
  } = useChatbot();

  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(
    localStorage.getItem("conversation_id")
  );
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const cancelRequest = () => {
    setIsTyping(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // ✅ LOAD CHAT HISTORY
  useEffect(() => {
    const loadChat = async () => {
      const storedId = localStorage.getItem("conversation_id");
      console.log("conversation_id:", storedId);

      if (!storedId) return;

      try {
        const res = await fetch(
          `http://localhost:5000/chatbot/history/${storedId}`,
          {
            headers: getAuthHeaders()
          }
        );

        if (!res.ok) throw new Error("Failed to fetch history");

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
  }, [setMessages]);

  // ✅ CREATE NEW CHAT
  const confirmNewChat = async () => {
    setShowConfirmDialog(false);

    try {
      const res = await fetch(
        "http://localhost:5000/chatbot/new_chat",
        {
          method: "POST",
          headers: getAuthHeaders()
        }
      );

      if (!res.ok) throw new Error("New chat failed");

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

  const closeChatbot = () => {
    if (typeof setIsOpen === "function") {
      setIsOpen(false);
    }
  };

  // ✅ SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim() || isTyping) return;

    const userInput = input;

    setMessages(prev => [...prev, { role: "user", text: userInput }]);
    setInput("");
    setIsTyping(true);

    let currentId = conversationId;

    try {
      if (!currentId) {
        const res = await fetch(
          "http://localhost:5000/chatbot/new_chat",
          {
            method: "POST",
            headers: getAuthHeaders()
          }
        );

        const data = await res.json();

        currentId = data.conversation_id;
        setConversationId(currentId);
        localStorage.setItem("conversation_id", currentId);
      }

      let url = "http://localhost:5000/chatbot/respond";
      let body = {};

      if (pendingQuestion) {
        url = "http://localhost:5000/chatbot/followup";
        body = {
          dream_id: dreamContext?.id || 1,
          question: pendingQuestion,
          answer: userInput,
          conversation_id: currentId,
          dream_context: dreamContext
        };
        setPendingQuestion(null);
      } else {
        body = {
          message: userInput,
          conversation_id: currentId,
          dream_context: dreamContext
        };
      }

      const res = await fetch(url, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(body)
      });

      if (!res.ok) throw new Error("Chat request failed");

      const data = await res.json();

      setTimeout(() => {
        setIsTyping(false);
        setMessages(prev => [
          ...prev,
          { role: "bot", text: data.response }
        ]);

        if (data.type === "question") {
          setPendingQuestion(data.response);
        }
      }, 1000);
    } catch (err) {
      console.error("Chatbot request failed:", err);
      setIsTyping(false);
    }
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
            >
              ↓
            </button>

            <button onClick={newChat} className="new-chat-btn">
              New Chat
            </button>

            <button
              onClick={closeChatbot}
              className="chatbot-close-btn"
            >
              ×
            </button>
          </div>
        </div>

        <div className="chatbot-messages" ref={messagesContainerRef}>
          {messages.map((m, i) => (
            <div key={i} className={`chatbot-message-row ${m.role}`}>
              {m.role === "bot" && <Mascot state="replying" small />}

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

                <button className="cancel-btn" onClick={cancelRequest}>
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

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