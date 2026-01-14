import React from "react";
import { useNavigate } from "react-router-dom";
import "./ActionCard.css";

export default function ActionCard({ title, subtitle, to, icon }) {
  const navigate = useNavigate();

  return (
    <div className="action-card" onClick={() => navigate(to)}>
      <div className="action-icon">{icon}</div>
      <div className="action-info">
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>
    </div>
  );
}
