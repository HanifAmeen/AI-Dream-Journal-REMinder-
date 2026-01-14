import React, { useEffect, useState, useRef } from "react";
import DreamForm from "./components/DreamForm";
import DreamList from "./components/DreamList";
import "./App.css";

function App() {
  const [dreams, setDreams] = useState([]);
  const listRef = useRef(null);

  // Fetch dreams from Flask
  const fetchDreams = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_dreams");
      if (!res.ok) throw new Error("Failed to fetch dreams");
      const data = await res.json();
      setDreams(data);
    } catch (err) {
      console.error("Error fetching dreams:", err);
      alert("Error fetching dreams. Make sure the backend is running.");
    }
  };

  // Add dream
  const addDream = async ({ title, content, mood }) => {
    try {
      const res = await fetch("http://127.0.0.1:5000/add_dream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content, mood }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Failed to save dream");
      }

      await res.json();
      await fetchDreams();
      scrollToBottom();

    } catch (err) {
      console.error("Error adding dream:", err);
      alert(`Error saving dream: ${err.message}`);
      throw err; // so DreamForm can handle loading/message
    }
  };

  // Delete dream
  const deleteDream = async (id) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/delete_dream/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete dream");
      await fetchDreams();
    } catch (err) {
      console.error("Error deleting dream:", err);
      alert(`Error deleting dream: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchDreams();
  }, []);

  const scrollToBottom = () => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  };

  return (
    <div className="dream-journal-page">
      <h1 className="dream-page-title">AI Dream Journal</h1>
      <div className="dream-dashboard">
        <div className="dream-form-wrapper">
          <DreamForm onAdd={addDream} />
        </div>
        <div className="dream-list-wrapper" ref={listRef}>
          <DreamList dreams={dreams} onDelete={deleteDream} />
        </div>
      </div>
    </div>
  );
}

export default App;
