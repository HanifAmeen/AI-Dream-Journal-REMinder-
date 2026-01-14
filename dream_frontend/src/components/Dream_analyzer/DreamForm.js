// DreamForm.js — FINAL (Backend-aligned, no dead fields)

import React, { useState, useRef } from "react";
import "./DreamForm.css";

function DreamForm({ onAdd }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const recognitionRef = useRef(null);
  const autoRestartRef = useRef(false);

  /* ------------------------------------------------------
     Initialize Web Speech API
  -------------------------------------------------------*/
  const initSpeechRecognition = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser.");
      return null;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    return recognition;
  };

  /* ------------------------------------------------------
     Start Mic
  -------------------------------------------------------*/
  const startRecognition = () => {
    const recognition = initSpeechRecognition();
    if (!recognition) return;

    recognitionRef.current = recognition;
    setIsRecording(true);
    setMessage("🎙️ Listening... Speak your dream");

    recognition.onresult = (event) => {
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript.trim() + " ";
        }
      }

      if (finalTranscript.trim()) {
        const cleaned = finalTranscript.trim();

        // Preserve sentence boundaries
        setContent((prev) =>
          prev ? prev + "\n" + cleaned : cleaned
        );
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setMessage("Mic error — try again.");
      setIsRecording(false);
      autoRestartRef.current = false;
    };

    recognition.onend = () => {
      if (isRecording && autoRestartRef.current) {
        recognition.start();
      } else {
        setIsRecording(false);
        setMessage("Stopped listening.");
        setTimeout(() => setMessage(""), 1500);
      }
    };

    autoRestartRef.current = true;
    recognition.start();
  };

  /* ------------------------------------------------------
     Stop Mic
  -------------------------------------------------------*/
  const stopRecognition = () => {
    if (recognitionRef.current) {
      autoRestartRef.current = false;
      recognitionRef.current.stop();
      setIsRecording(false);

      setMessage("Stopped listening.");
      setTimeout(() => setMessage(""), 1500);
    }
  };

  const handleMicClick = () => {
    isRecording ? stopRecognition() : startRecognition();
  };

  /* ------------------------------------------------------
     Submit Form
  -------------------------------------------------------*/
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title || !content) {
      setMessage("Title and content are required.");
      setTimeout(() => setMessage(""), 2000);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      // 🔑 ONLY send what backend actually uses
      await onAdd({ title, content });

      setTitle("");
      setContent("");
      setMessage("Dream saved!");
      setTimeout(() => setMessage(""), 2000);
    } catch (err) {
      console.error("Error saving dream:", err);
      setMessage("Error saving dream.");
      setTimeout(() => setMessage(""), 2000);
    } finally {
      setLoading(false);
    }
  };

  /* ------------------------------------------------------
     Clear Form
  -------------------------------------------------------*/
  const handleClear = () => {
    setTitle("");
    setContent("");
    setMessage("Cleared form.");
    setTimeout(() => setMessage(""), 1500);
  };

  /* ------------------------------------------------------
     Auto-Resize Textarea
  -------------------------------------------------------*/
  const autoResize = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  };

  return (
    <div className="dream-form-container">
      <h2 className="dream-form-title">Add Your Dream</h2>

      <form onSubmit={handleSubmit} className="dream-form">
        <input
          type="text"
          placeholder="Dream title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="dream-input"
        />

        <textarea
          placeholder="Write or speak your dream..."
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            autoResize(e);
          }}
          required
          className="dream-textarea"
          rows={1}
        />

        <div
          style={{
            display: "flex",
            gap: "10px",
            justifyContent: "center",
            marginTop: "10px",
          }}
        >
          <button
            type="submit"
            className="dream-button"
            disabled={loading}
          >
            {loading ? "Saving..." : "Save Dream"}
          </button>

          <button
            type="button"
            onClick={handleMicClick}
            className={`dream-button mic-button ${
              isRecording ? "recording" : ""
            }`}
          >
            {isRecording ? "🛑 Stop" : "🎤 Speak"}
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="dream-button"
            style={{
              background:
                "linear-gradient(to right, #424242, #212121)",
            }}
          >
            Clear
          </button>
        </div>
      </form>

      {loading && <div className="loader"></div>}
      {message && (
        <p className="dream-message">{message}</p>
      )}
    </div>
  );
}

export default DreamForm;
