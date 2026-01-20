import { createContext, useContext, useState } from "react";

const ChatbotContext = createContext();

export function ChatbotProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [pendingQuestion, setPendingQuestion] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  const toggleChat = () => setIsOpen((prev) => !prev);

  return (
    <ChatbotContext.Provider
      value={{
        isOpen,
        toggleChat,
        messages,
        setMessages,
        pendingQuestion,
        setPendingQuestion,
        isTyping,
        setIsTyping
      }}
    >
      {children}
    </ChatbotContext.Provider>
  );
}

export function useChatbot() {
  return useContext(ChatbotContext);
}
