import React, { useState } from "react";
import "./DreamList.css";

const fmt = (n) =>
  typeof n === "number" ? n.toFixed(3) : "—";

const cap = (s) =>
  typeof s === "string" && s.length
    ? s.charAt(0).toUpperCase() + s.slice(1)
    : "—";

export default function DreamList({ dreams = [] }) {
  const [open, setOpen] = useState({});

  const toggle = (id) =>
    setOpen((p) => ({ ...p, [id]: !p[id] }));

  // Interpretation rendering function
  const renderInterpretation = (text) => {
    if (typeof text !== "string") return null;

    const lines = text.split("\n").map(l => l.trim());
    const blocks = [];
    let listBuffer = [];

    lines.forEach((line) => {
      if (line.startsWith("- ")) {
        listBuffer.push(line.replace("- ", ""));
      } else {
        if (listBuffer.length) {
          blocks.push({ type: "list", items: [...listBuffer] });
          listBuffer = [];
        }
        if (line) {
          blocks.push({ type: "text", content: line });
        }
      }
    });

    if (listBuffer.length) {
      blocks.push({ type: "list", items: [...listBuffer] });
    }

    return blocks.map((block, idx) => {
      if (block.type === "text") {
        return (
          <p key={idx} className="interpretation-paragraph">
            {block.content}
          </p>
        );
      }

      if (block.type === "list") {
        return (
          <ul key={idx} className="interpretation-list">
            {block.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        );
      }

      return null;
    });
  };

  if (!dreams.length) {
    return (
      <div className="dream-list-container">
        <div className="empty-state">
          <div className="empty-icon">🌙</div>
          <h3>No analyzed dreams yet</h3>
          <p>Add your first dream to begin dream analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dream-list-container">
      {dreams.map((dream, i) => {
        const id = dream.id ?? i;
        const symbols = dream.symbols || {};
        const arc = dream.emotional_arc || {};
        const confidence = dream.confidence || {};
        const isOpen = open[id];

        return (
          <div key={id} className="dream-card">
            {/* Header */}
            <div className="dream-header" onClick={() => toggle(id)}>
              <div className="dream-title-section">
                <h3 className="dream-title">Dream #{dreams.length - i}</h3>
                <span className="dream-date">{new Date(dream.date).toLocaleDateString()}</span>
              </div>
              <div className="dream-mood-badge">
                {cap(dream.mood || "unknown")}
              </div>
              <div className="expand-icon">
                {isOpen ? "▲" : "▼"}
              </div>
            </div>

            {/* Content */}
            {isOpen && (
              <div className="dream-content">
                {/* Emotion Analysis */}
                <div className="analysis-section">
                  <h4>🎭 Emotion Analysis</h4>
                  <div className="metric-row">
                    <div className="metric">
                      <span className="metric-label">Dominant Emotion</span>
                      <span className="metric-value">{cap(dream.mood)}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Confidence</span>
                      <span className="metric-value">{fmt(confidence?.overall)}</span>
                    </div>
                  </div>

                  {arc?.trajectory && (
                    <div className="trajectory">
                      <div className="trajectory-path">
                        {arc.trajectory?.map((emotion, idx) => (
                          <span
                            key={idx}
                            className="trajectory-node"
                            style={{ '--intensity': arc.shift_intensity || 0 }}
                          >
                            {cap(emotion)}
                          </span>
                        ))}
                      </div>
                      <p className="trajectory-desc">{arc.trajectory_description}</p>
                    </div>
                  )}
                </div>

                {/* Symbols */}
                <div className="analysis-section">
                  <h4>🔮 Top Symbols</h4>
                  {Object.keys(symbols).length ? (
                    <div className="symbols-grid">
                      {Object.entries(symbols)
                        .sort(([,a], [,b]) => b - a)
                        .map(([symbol, score]) => (
                          <div key={symbol} className="symbol-item">
                            <span className="symbol-name">{symbol}</span>
                            <div className="symbol-bar">
                              <div
                                className="symbol-fill"
                                style={{ width: `${Math.min(score * 100, 100)}%` }}
                              />
                              <span className="symbol-score">{fmt(score)}</span>
                            </div>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <p className="no-data">No symbols detected</p>
                  )}
                </div>

                {/* Dream Text */}
                <div className="analysis-section">
                  <h4>💭 Dream Content</h4>
                  <div className="dream-text">{dream.content}</div>
                </div>

                {/* Interpretation — FIXED WITH renderInterpretation */}
                <div className="analysis-section">
                  <h4>✨ Interpretation</h4>
                  <div className="interpretation">
                    {renderInterpretation(dream.interpretation)}
                  </div>
                </div>

                {/* Confidence & Trauma */}
                <div className="analysis-section">
                  <h4>📊 Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="metric-value-lg">{fmt(confidence.symbol)}</div>
                      <div className="metric-label">Symbol Confidence</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-value-lg">{fmt(confidence.overall)}</div>
                      <div className="metric-label">Overall Confidence</div>
                    </div>
                    <div className="metric-card trauma">
                      <div className="metric-value-lg">{fmt(dream.trauma_score)}</div>
                      <div className="metric-label">
                        Trauma Signal
                        <span className={`trauma-badge ${
                          dream.trauma_score >= 15 ? 'elevated' : 'low'
                        }`}>
                          {dream.trauma_score >= 15 ? 'Elevated' : 'Low'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="dream-footer">
                  <span>Analysis v{dream.analysis_version}</span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
