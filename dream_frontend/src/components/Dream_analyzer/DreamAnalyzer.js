import React, { useEffect } from "react";
import DreamForm from "./DreamForm";
import DreamList from "./DreamList";
import "./DreamPage.css";
import { useChatbot } from "../../context/ChatbotContext";

export default function DreamAnalyzer({ dreams, onAdd, onDelete, listRef }) {
  const { setMessages } = useChatbot();

  // 🔹 Inject dream context when dreams update
  useEffect(() => {
    if (!dreams || dreams.length === 0) return;

    const latestDream = dreams[0];

    setMessages([
      {
        role: "bot",
        text:
          "I can help you explore this dream further — ask about symbols, emotions, or patterns you notice."
      }
    ]);
  }, [dreams]);

  return (
    <div className="dream-journal-page">
      <h1 className="dream-page-title">AI Dream Analyzer</h1>

      <div className="dream-dashboard">
        <div className="dream-form-wrapper">
          <DreamForm onAdd={onAdd} />
        </div>

        <div className="dream-list-wrapper" ref={listRef}>
          <DreamList dreams={dreams} onDelete={onDelete} />
        </div>
      </div>
    </div>
  );
}
