import React, { useState } from "react";
import "./DreamList.css";

const fmt = (n) =>
  typeof n === "number" ? n.toFixed(2) : "—";

// 🔥 NEW: Symbol strength labels
const strength = (score) => {
  if (score > 0.75) return "Very strong";
  if (score > 0.5) return "Strong";
  if (score > 0.35) return "Moderate";
  return "Weak";
};

const cap = (s) =>
  typeof s === "string" && s.length
    ? s.charAt(0).toUpperCase() + s.slice(1)
    : "—";

export default function DreamList({ dreams = [] }) {
  const [open, setOpen] = useState({});
  // 🔥 NEW: Symbol explanation toggle state
  const [showSymbolHelp, setShowSymbolHelp] = useState({});
  // ✅ NEW: Individual metric help state (per dream, per metric)
  const [showMetricHelp, setShowMetricHelp] = useState({});
  // ✅ NEW: Emotion breakdown toggle state (per dream)
  const [showEmotionBreakdown, setShowEmotionBreakdown] = useState({});
  // 🔥 NEW: All symbols toggle state (per dream) ✅ ADDED
  const [showAllSymbols, setShowAllSymbols] = useState({});
  // 🔥 NEW: Symbol prominence toggle ✅ CHANGE 1
  const [showAllProminence, setShowAllProminence] = useState({});

  const toggle = (id) =>
    setOpen((p) => ({ ...p, [id]: !p[id] }));

  // 🔥 NEW: Toggle symbol explanation for specific dream
  const toggleSymbolHelp = (id) => {
    setShowSymbolHelp((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // 🔥 NEW: Toggle all symbols for specific dream ✅ ADDED
  const toggleAllSymbols = (id) => {
    setShowAllSymbols((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // ✅ NEW: Toggle individual metric help
  const toggleMetricHelp = (id, metric) => {
    setShowMetricHelp((prev) => {
      const dreamHelp = prev[id] || {};
      return {
        ...prev,
        [id]: {
          ...dreamHelp,
          [metric]: !dreamHelp[metric],
        },
      };
    });
  };

  // ✅ NEW: Toggle emotion breakdown
  const toggleEmotionBreakdown = (id) => {
    setShowEmotionBreakdown((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // 🔥 NEW: Toggle all prominence ✅ CHANGE 2
  const toggleAllProminence = (id) => {
    setShowAllProminence((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // 🔥 NEW: Delete Handler
  const handleDelete = async (id) => {
    const confirmDelete = window.confirm("Delete this dream?");
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`http://localhost:5000/delete_dream/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Delete failed");

      // reload page or refetch dreams
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert("Failed to delete dream");
    }
  };

  // Interpretation rendering function - ✅ UPDATED
  const renderInterpretation = (text) => {
    if (typeof text !== "string") return null;

    // 🔥 FIXED: Remove ** markdown bold symbols
    const lines = text
      .replace(/\*\*/g, "")
      .split("\n")
      .map((l) => l.trim());

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
        const showHelp = showSymbolHelp[id];
        // ✅ NEW: Individual metric help state
        const showMetricInfo = showMetricHelp[id] || {};
        // ✅ NEW: Emotion breakdown state
        const showEmotionBreakdownState = showEmotionBreakdown[id];
        // 🔥 NEW: All symbols state ✅ ADDED
        const showAllSymbolsState = showAllSymbols[id];
        // 🔥 NEW: Symbol prominence state ✅ CHANGE 3
        const showAllProminenceState = showAllProminence[id];
        
        // 🔥 Calculate dominant emotion from distribution
        let dominantEmotion = dream.mood;
        let dominantScore = null;
        if (arc?.emotion_distribution) {
          const sorted = Object.entries(arc.emotion_distribution)
            .sort((a, b) => b[1] - a[1]);
          if (sorted.length) {
            dominantEmotion = sorted[0][0];
            dominantScore = sorted[0][1];
          }
        }

        return (
          <div key={id} className="dream-card">
            {/* 🔥 NEW HEADER STRUCTURE */}
            <div className="dream-header">
              <div
                className="dream-title-section"
                onClick={() => toggle(id)}
              >
                <div className="dream-title-row">
                  <h3 className="dream-title">
                    Dream #{dreams.length - i} — {dream.title || "Untitled"}
                  </h3>

                  <span className="dream-mood-badge">
                    {cap(dream.mood || "unknown")}
                  </span>
                </div>

                <span className="dream-date">
                  {new Date(dream.date).toLocaleDateString()}
                </span>
              </div>

              <div className="dream-actions">
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(id);
                  }}
                >
                  🗑
                </button>

                <div
                  className="expand-icon"
                  onClick={() => toggle(id)}
                >
                  {isOpen ? "▲" : "▼"}
                </div>
              </div>
            </div>

            {/* Content - REORDERED */}
            {isOpen && (
              <div className="dream-content">
                {/* 1️⃣ DREAM CONTENT FIRST */}
                <div className="analysis-section">
                  <h4>💭 Dream Content</h4>
                  <div className="dream-text">{dream.content}</div>
                </div>

                {/* 2️⃣ EMOTION ANALYSIS SECOND - ✅ ALL CHANGES APPLIED */}
                <div className="analysis-section">
                  
                    <h4>🎭 Emotion Analysis</h4>
                 
                  <div className="metric-row">
                    <div className="metric dominant-emotion">
                      <span className="metric-label">Dominant Emotion</span>
                      
                      <span className="metric-value">
                         <button
                          className="emotion-toggle"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleEmotionBreakdown(id);
                          }}
                        >
                          {showEmotionBreakdownState ? "Hide" : "All"}
                        </button>
                        {cap(dominantEmotion)}
                      </span>
                    </div>

                    <div className="metric">
                      <span className="metric-label">Emotion Strength</span>
                      <span className="metric-value">
                        {dominantScore !== null ? (dominantScore * 100).toFixed(1) : "—"}%
                      </span>
                    </div>
                  </div>

                  {showEmotionBreakdownState && arc?.emotion_distribution && (
                    <div className="emotion-breakdown">
                      {Object.entries(arc.emotion_distribution)
                        .sort((a, b) => b[1] - a[1])
                        .map(([emotion, score]) => (
                          <div key={emotion} className="emotion-row">
                            <span>{cap(emotion)}</span>
                            <span>{(score * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                    </div>
                  )}

                  {arc?.trajectory && (
                    <div className="trajectory">
                      <div className="trajectory-path">
                        {arc.trajectory?.map((emotion, idx) => (
                          <span
                            key={idx}
                            className="trajectory-node"
                            style={{ "--intensity": arc.shift_intensity || 0 }}
                          >
                            {cap(emotion)}
                          </span>
                        ))}
                      </div>
                      <p className="trajectory-desc">
                        {arc.trajectory_description}
                      </p>
                    </div>
                  )}
                </div>

                {/* 3️⃣ SYMBOLS THIRD + "All" BUTTON ✅ FULLY IMPLEMENTED */}
                <div className="analysis-section">
                  <div className="symbols-header">
                    <h4>🔮 Top Symbols</h4>

                    <div className="symbols-buttons">
                      <button
                        className="symbol-help-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSymbolHelp(id);
                        }}
                        title="Symbol scoring explanation"
                      >
                        ?
                      </button>
                      
                      {/* 🔥 NEW: All Symbols Button ✅ IMPLEMENTED */}
                      <button
                        className="all-symbols-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleAllSymbols(id);
                        }}
                        title="Show all detected symbols"
                      >
                        {showAllSymbolsState ? "Top" : "All"}
                      </button>
                    </div>
                  </div>

                  {Object.keys(symbols).length ? (
                    <div className="symbols-grid">
                      {Object.entries(symbols)
                        .sort(([, a], [, b]) => b - a)
                        // 🔥 KEY CHANGE: Show top 3 OR all symbols ✅ IMPLEMENTED
                        .slice(0, showAllSymbolsState ? undefined : 3)
                        .map(([symbol, score]) => (
                          <div key={symbol} className="symbol-item">
                            <span className="symbol-name">{symbol}</span>

                            <div className="symbol-bar">
                              <div className="symbol-fill">
                                <div
                                  className="symbol-fill-inner"
                                  style={{
                                    width: `${Math.min(score * 100, 100)}%`,
                                  }}
                                />
                              </div>

                              <span className="symbol-score">
                                {fmt(score)} ({strength(score)})
                              </span>
                            </div>
                          </div>
                        ))}

                      {/* 🔥 NEW: All symbols note */}
                      {showAllSymbolsState && (
                        <div className="all-symbols-note">
                          Showing all {Object.keys(symbols).length} detected symbols
                        </div>
                      )}

                      <div className={`symbol-help ${showHelp ? "show" : ""}`}>
                        Symbol strength shows how strongly an image appears in your dream
                        narrative. Higher scores mean the symbol was more prominent or
                        emotionally connected.
                      </div>
                    </div>
                  ) : (
                    <p className="no-data">No symbols detected</p>
                  )}
                </div>

                {/* 4️⃣ INTERPRETATION FOURTH */}
                <div className="analysis-section">
                  <h4>✨ Interpretation</h4>
                  <div className="interpretation">
                    {renderInterpretation(dream.interpretation)}
                  </div>
                </div>

                {/* ✅ NEW: METRICS SECTION - Personalization block REMOVED */}
                <div className="analysis-section">
                  
                    <h4>📊 Metrics</h4>
                

                  <div className="metrics-grid">
                    {/* 1️⃣ Symbol Prominence – ✅ ALL 6 CHANGES APPLIED */}
                    <div className="metric-card">
                      <div className="metric-header">
                        <span className="metric-title">Symbol Prominence</span>

                        <div className="metric-header-actions">
                          {/* ✅ CHANGE 4: "All" button + "?" button */}
                          <button
                            className="all-symbols-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleAllProminence(id);
                            }}
                          >
                            {showAllProminenceState ? "Top" : "All"}
                          </button>

                          <button
                            className="metric-help-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleMetricHelp(id, "symbol_prominence");
                            }}
                          >
                            ?
                          </button>
                        </div>
                      </div>

                      {dream.symbol_prominence && (
                        <div className="symbol-prominence">
                          {/* ✅ CHANGE 5: Slice to top 3 by default */}
                          {Object.entries(dream.symbol_prominence)
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, showAllProminenceState ? undefined : 3)
                            .map(([sym, val]) => (
                              <div key={sym} className="symbol-row">
                                <span className="symbol-name">{sym}</span>
                                <span className="symbol-value">{val}%</span>
                              </div>
                            ))}

                          {/* ✅ CHANGE 6: Optional "Showing all X" note */}
                          {showAllProminenceState && (
                            <div className="all-symbols-note">
                              Showing all {Object.keys(dream.symbol_prominence).length} symbols
                            </div>
                          )}

                          <div className="symbol-average">
                            Average Symbol Prominence
                            <span>{dream.avg_symbol_prominence}%</span>
                          </div>
                        </div>
                      )}

                      <div
                        className={`metric-help ${
                          showMetricInfo?.symbol_prominence ? "show" : ""
                        }`}
                      >
                        Symbol prominence measures how strongly each symbol
                        contributes to the dream's imagery. Scores are
                        calculated using semantic relevance, repetition, and
                        narrative position within the dream text.
                      </div>
                    </div>

                    {/* 2️⃣ Overall Confidence – UNCHANGED */}
                    <div className="metric-card">
                      <div className="metric-header">
                        <span className="metric-title">Overall Confidence</span>
                        <button
                          className="metric-help-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleMetricHelp(id, "overall");
                          }}
                        >
                          ?
                        </button>
                      </div>

                      <div className="metric-value-lg">
                        {fmt(confidence?.overall)}%
                      </div>

                      <div
                        className={`metric-help ${
                          showMetricInfo?.overall ? "show" : ""
                        }`}
                      >
                        Overall confidence reflects how reliably the system can
                        interpret the dream based on emotional patterns and
                        symbol strength.
                      </div>
                    </div>

                    {/* 3️⃣ Trauma Signal – REPLACED STRUCTURE */}
                    <div className="metric-card trauma">
                      <div className="metric-header">
                        <span className="metric-title">Trauma Signal</span>

                        <div className="trauma-meta">
                          <span
                            className={`trauma-badge ${
                              dream.trauma_score >= 15 ? "elevated" : "low"
                            }`}
                          >
                            {dream.trauma_score >= 15
                              ? "Elevated"
                              : "Low"}
                          </span>

                          <button
                            className="metric-help-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleMetricHelp(id, "trauma");
                            }}
                          >
                            ?
                          </button>
                        </div>
                      </div>

                      <div className="metric-value-lg">
                        {fmt(dream.trauma_score)}
                      </div>

                      <div
                        className={`metric-help ${
                          showMetricInfo?.trauma ? "show" : ""
                        }`}
                      >
                        Trauma signal estimates whether the dream contains
                        emotional patterns associated with distress such as
                        threat, confinement, or unresolved fear.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="dream-footer">
                  {/* <span>Analysis v{dream.analysis_version}</span> */}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
