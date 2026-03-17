import { useState, useEffect } from "react";
import "./helpGuide.css";

export default function HelpGuide() {

  const [showGuide, setShowGuide] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  /* -----------------------------
     Check if help was hidden
  ------------------------------*/
  useEffect(() => {

    const hidden = localStorage.getItem("hide_dream_help");

    if (!hidden) {
      setShowGuide(true);   // Auto open first time
    }

  }, []);


  /* -----------------------------
     Close modal
  ------------------------------*/
  const closeGuide = () => {

    if (dontShowAgain) {
      localStorage.setItem("hide_dream_help", "true");
    }

    setShowGuide(false);

  };


  return (
    <>

      {/* HELP BUTTON (Always visible) */}
      <button
        className="dream-help-button floating-help"
        onClick={() => setShowGuide(true)}
        type="button"
        title="Need Help?"
      >
        Need Help?
      </button>


      {/* HELP MODAL */}
      {showGuide && (

        <div
          className="dream-help-overlay"
          onClick={closeGuide}
        >

          <div
            className="dream-help-modal"
            onClick={(e) => e.stopPropagation()}
          >

            <h2>How to Use the Dream Analyzer</h2>

            <div className="dream-help-steps">

              <h3>Steps</h3>

              <ol>
                <li>Give your dream a short title.</li>
                <li>Describe the dream in the text box.</li>
                <li>Include emotions, people, places, and objects you noticed.</li>
                <li>Click <strong>Analyze Dream</strong>.</li>
                <li>Review the interpretation and insights.</li>
              </ol>


              <hr className="help-divider" />


              <h3>Using the Voice Recording Feature</h3>

              <ul>
                <li>Click the <strong>🎤 Speak</strong> button.</li>
                <li>Describe your dream naturally like telling a story.</li>
                <li>Your speech will automatically convert into text.</li>
                <li>Click <strong>🛑 Stop</strong> when finished.</li>
                <li>You can edit the text before analyzing.</li>
              </ul>


              <hr className="help-divider" />


              <h3>Best Ways to Describe Your Dream</h3>

              <ul>
                <li>Write dreams in <strong>first person</strong> (example: "I was walking through a forest").</li>
                <li>Describe what you <strong>saw, heard, and felt</strong>.</li>
                <li>Mention important <strong>symbols or objects</strong>.</li>
                <li>Include emotional reactions during the dream.</li>
                <li>If you mention someone, explain who they are.</li>
              </ul>


              <hr className="help-divider" />


              <h3>Tips for Better Analysis</h3>

              <ul>
                <li>Write dreams like a short story.</li>
                <li>Longer descriptions produce better interpretations.</li>
                <li>Focus on unusual or emotional moments.</li>
                <li>Describe scene changes clearly.</li>
              </ul>

            </div>


            {/* MODAL FOOTER */}
            <div className="dream-help-options">

              <label>
                <input
                  type="checkbox"
                  checked={dontShowAgain}
                  onChange={(e) => setDontShowAgain(e.target.checked)}
                />
                Don't show this again
              </label>


              <button
                className="dream-help-close"
                onClick={closeGuide}
              >
                Got it
              </button>

            </div>

          </div>

        </div>

      )}

    </>
  );
}