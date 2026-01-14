import React, { useState } from "react";
import "./DreamVisualizer.css";

function DreamVisualizer() {
  const [dream, setDream] = useState("");
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateImages = async () => {
    if (!dream.trim()) return;

    setLoading(true);
    setImages([]);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("You are not logged in.");
        return;
      }

      const res = await fetch("http://127.0.0.1:5000/visualize_dream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ dream }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Image generation failed");
      }

      const data = await res.json();
      if (Array.isArray(data.images)) {
        setImages(data.images);
      } else {
        throw new Error("Invalid image response");
      }
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearDream = () => {
    setDream("");
    setImages([]);
    setError(null);
  };

  const deleteImage = (index) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="visualizer-container">
      <h1 className="visualizer-title">Dream Visualizer</h1>

      <div className="input-card">
        <textarea
          className="dream-input-visualizer"
          placeholder="Describe your dream in detail… What did you see, feel, or experience?"
          value={dream}
          onChange={(e) => setDream(e.target.value)}
        />

        <div className="input-actions">
          <button
            className="generate-btn"
            onClick={generateImages}
            disabled={loading}
          >
            {loading ? "Generating…" : "Generate Images"}
          </button>

          <button
            className="clear-btn"
            onClick={clearDream}
            disabled={loading && !dream}
          >
            Clear
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading-spinner">
          Visualizing your dream scenes…
        </div>
      )}

      {error && <div className="error-text">{error}</div>}

      {images.length > 0 && (
        <div className="image-gallery">
          {images.map((url, i) => (
            <div key={i} className="image-card">
              <img
                src={url}
                alt={`Dream scene ${i + 1}`}
                className="dream-image"
                loading="lazy"
              />
              <div className="image-overlay">
                <span>Scene {i + 1}</span>
                <button
                  className="delete-img-btn"
                  onClick={() => deleteImage(i)}
                  title="Remove image"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DreamVisualizer;
