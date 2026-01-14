// DreamAnalyzer.js
import React from "react";
import DreamForm from "./DreamForm";
import DreamList from "./DreamList";
import "./DreamPage.css";

export default function DreamAnalyzer({ dreams, onAdd, onDelete, listRef }) {
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
