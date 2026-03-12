import React, { useState, useEffect, useCallback } from "react";
import "./DreamVisualizer.css";

function DreamVisualizer() {
  const [dream, setDream] = useState("");
  const [dreamBatches, setDreamBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // ✅ FIXED: Memoized fetch function to prevent stale closures
  const fetchWithAuth = useCallback(async (url, options = {}) => {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No authentication token found");

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return response.json();
  }, []);

  // Load batched images on mount
  useEffect(() => {
    const loadDreamBatches = async () => {
      try {
        setError(null);
        const batches = await fetchWithAuth("http://127.0.0.1:5000/get_visualizations");
        setDreamBatches(batches || []);
      } catch (err) {
        console.error("Failed to load dream batches:", err);
        setError("Failed to load your dream collections");
      }
    };

    loadDreamBatches();
  }, [fetchWithAuth]);

  const generateImages = async () => {
    if (!dream.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchWithAuth("http://127.0.0.1:5000/visualize_dream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dream }),
      });

      if (data.images && data.dream_batch_id) {
        const newBatch = {
          id: data.dream_batch_id,
          images: data.images.map(url => ({ url: url })),
          count: data.images.length,
          created_at: new Date().toISOString()
        };
        setDreamBatches(prev => [newBatch, ...prev]);
        setDream("");
      }
    } catch (err) {
      console.error("Image generation failed:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearDream = () => {
    setDream("");
    setError(null);
  };

  const openImageModal = useCallback((url, batchIndex, imageIndex) => {
    setSelectedImage({ url, batchIndex, imageIndex });
  }, []);

  const closeImageModal = useCallback(() => {
    setSelectedImage(null);
  }, []);

  const confirmBatchDelete = useCallback((batchId) => {
    setDeleteConfirm(batchId);
  }, []);

  const cancelDelete = useCallback(() => {
    setDeleteConfirm(null);
  }, []);

  const deleteBatch = useCallback(async (batchId) => {
    try {
      await fetchWithAuth(`http://127.0.0.1:5000/delete_dream_batch/${batchId}`, {
        method: "DELETE",
      });
      setDreamBatches(prev => prev.filter(batch => batch.id !== batchId));
    } catch (err) {
      console.error("Failed to delete batch:", err);
      setError("Failed to delete dream batch");
    } finally {
      setDeleteConfirm(null);
    }
  }, [fetchWithAuth]);

  // ✅ Handle Enter key for textarea
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      e.preventDefault();
      generateImages();
    }
  };

  return (
    <div className="visualizer-container">
      {/* Hero Header */}
      <div className="hero-header">
        <div className="hero-content">
          <h1 className="visualizer-title">Dream Visualizer</h1>
          <p className="hero-subtitle">
            Transform your dreams into stunning artwork with AI magic ✨
          </p>
        </div>
      </div>

      {/* Input Section */}
      <div className="input-card glass-effect">
        <div className="input-header">
          <span className="input-icon">💭</span>
          <h2>Create New Dream</h2>
        </div>
        <textarea
          className="dream-input-visualizer"
          placeholder="Describe your dream... I was flying through golden clouds..."
          value={dream}
          onChange={(e) => setDream(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={4}
          disabled={loading}
        />
        <div className="input-actions">
          <button
            className="generate-btn gradient-btn"
            onClick={generateImages}
            disabled={loading || !dream.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span> Generating Magic…
              </>
            ) : (
              "✨ Generate Dream Art"
            )}
          </button>
          <button 
            className="clear-btn secondary-btn" 
            onClick={clearDream}
            disabled={loading}
          >
            🗑️ Clear Input
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="error-card glass-effect">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="loading-container glass-effect">
          <div className="loading-spinner-large">
            <div className="dream-pulse"></div>
          </div>
          <p className="loading-text">Crafting your dream visions...</p>
        </div>
      )}

      {/* Dream Batches Gallery */}
      {dreamBatches.length > 0 && (
        <div className="batches-container">
          <div className="gallery-header">
            <span className="gallery-icon">🖼️</span>
            <h2>Your Dream Collections ({dreamBatches.length})</h2>
          </div>
          
          {dreamBatches.map((batch, batchIndex) => (
            <div key={batch.id} className="dream-batch">
              <div className="batch-header">
                <div className="batch-left">
                  <h3 className="batch-title">Dream #{batchIndex + 1}</h3>
                  <span className="batch-meta">
                    {batch.count} scenes • {new Date(batch.created_at).toLocaleDateString()}
                  </span>
                </div>
                <button
                  className="batch-delete-btn"
                  onClick={() => confirmBatchDelete(batch.id)}
                  title="Delete entire dream batch"
                >
                  Delete
                </button>
              </div>
              
              <div className="image-gallery">
                {batch.images?.map((img, i) => (
                  <div key={`${batch.id}-${i}`} className="image-card glass-effect">
                    <div 
                      className="image-wrapper"
                      role="button"
                      tabIndex={0}
                      onClick={() => openImageModal(img.url, batchIndex, i)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          openImageModal(img.url, batchIndex, i);
                        }
                      }}
                    >
                      <img
                        src={`${img.url}?t=${Date.now()}`}
                        alt={`Dream ${batchIndex + 1} - Scene ${i + 1}`}
                        className="dream-image"
                        loading="lazy"
                      />
                      <div className="image-shimmer"></div>
                    </div>
                    <div className="image-overlay">
                      <span className="scene-label">
                        Scene {i + 1}/{batch.count}
                      </span>
                    </div>
                  </div>
                )) || null}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No batches message */}
      {dreamBatches.length === 0 && !loading && (
        <div className="empty-state glass-effect">
          <span className="empty-icon">🌙</span>
          <h3>No Dream Collections Yet</h3>
          <p>Describe your first dream above to create beautiful artwork!</p>
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div className="modal-overlay" onClick={closeImageModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="modal-close" 
              onClick={closeImageModal}
              aria-label="Close modal"
            >
              ×
            </button>
            <img 
              src={selectedImage.url} 
              alt="Enlarged dream scene" 
              className="modal-image" 
            />
            <div className="modal-info">
              <span>
                Dream #{selectedImage.batchIndex + 1} • Scene {selectedImage.imageIndex + 1}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Batch Delete Confirmation */}
      {deleteConfirm && (
        <div className="confirm-overlay">
          <div className="confirm-card glass-effect">
            <h3>Delete Entire Dream?</h3>
            <p>
              This will remove all{" "}
              {dreamBatches.find(b => b.id === deleteConfirm)?.count || 0} images 
              from this dream collection.
            </p>
            <div className="confirm-actions">
              <button
                className="confirm-delete gradient-danger"
                onClick={() => deleteBatch(deleteConfirm)}
              >
                🗑️ Yes, Delete Dream
              </button>
              <button
                className="confirm-cancel secondary-btn"
                onClick={cancelDelete}
              >
                ❌ Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DreamVisualizer;
