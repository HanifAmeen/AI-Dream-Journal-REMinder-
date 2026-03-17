import React, { useState, useRef } from "react";
import "./DreamForm.css";
import HelpGuide from "./helpGuide";

function DreamForm({ onAdd }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [useProfile, setUseProfile] = useState(true);

  const recognitionRef = useRef(null);
  const autoRestartRef = useRef(false);

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

        setContent((prev) =>
          prev ? prev + "\n" + cleaned : cleaned
        );
      }
    };

    recognition.onerror = (event) => {
      console.error(event.error);
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
      await onAdd({
        title,
        content,
        use_profile: useProfile
      });

      setTitle("");
      setContent("");

      setMessage("Dream saved!");
      setTimeout(() => setMessage(""), 2000);

    } catch (err) {
      console.error(err);
      setMessage("Error saving dream.");
      setTimeout(() => setMessage(""), 2000);

    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setTitle("");
    setContent("");

    setMessage("Cleared form.");
    setTimeout(() => setMessage(""), 1500);
  };

  const autoResize = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  };

  return (
    <>
      {/* Help Guide Button + Modal */}
      <HelpGuide />

      <div className="dream-form-container">

        <div className="dream-form-header">
          <h2 className="dream-form-title">
            Add Your Dream
          </h2>
        </div>

        <form
          onSubmit={handleSubmit}
          className="dream-form"
        >

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

          <div className="dream-buttons">

            <button
              type="submit"
              className="dream-button"
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Dream"}
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
              className="dream-button clear-button"
            >
              Clear
            </button>

          </div>

          <div className="profile-toggle">
            <label>
              <input
                type="checkbox"
                checked={useProfile}
                onChange={() => setUseProfile(!useProfile)}
              />
              Personalize interpretation using my profile
            </label>
          </div>

        </form>

        {loading && (
          <div className="loader"></div>
        )}

        {message && (
          <p className="dream-message">
            {message}
          </p>
        )}

      </div>
    </>
  );
}

export default DreamForm;