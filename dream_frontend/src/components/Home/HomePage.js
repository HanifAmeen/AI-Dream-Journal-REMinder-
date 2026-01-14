import React, { useEffect, useState, useRef } from "react";
import "./home.css";
import ActionCard from "../Common/ActionCard/ActionCard";

export default function Home() {
  const user = JSON.parse(localStorage.getItem("user"));
  const justLoggedIn = localStorage.getItem("justLoggedIn") === "true";
  
  const [title, setTitle] = useState("REMinder");
  const [fade, setFade] = useState(true);
  const timerRef = useRef(null);

  // Initial title setup
  React.useEffect(() => {
    if (justLoggedIn && user?.username) {
      setTitle(`Welcome Back ${user.username}`);
    }
  }, []);

  // Animation effect - FIXED
  useEffect(() => {
    if (!justLoggedIn) return;

    console.log("Animation started - justLoggedIn:", justLoggedIn);
    
    // Cancel any existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // 10 SECOND timer
    timerRef.current = setTimeout(() => {
      console.log("Fading out welcome message");
      setFade(false);

      // Fade out complete → switch title → fade in
      setTimeout(() => {
        console.log("Switching to REMinder");
        setTitle("REMinder");
        setFade(true);
        localStorage.setItem("justLoggedIn", "false");
      }, 600);
    }, 10000); // CHANGED FROM 100ms to 10s

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [justLoggedIn]);

  const features = [
    { title: "Add a Dream", subtitle: "Record your dream instantly", to: "/add-dream", icon: "✨" },
    { title: "My Dreams", subtitle: "Browse your dream journal", to: "/dreams", icon: "🌙" },
    { title: "AI Analyzer", subtitle: "Unlock dream meanings", to: "/dream-analyzer", icon: "🧠" },
    { title: "Visualizer", subtitle: "See your dreams alive", to: "/visualizer", icon: "🔮" },
    { title: "Insights", subtitle: "Discover patterns", to: "/insights", icon: "📊" },
    { title: "Profile", subtitle: "Manage settings", to: "/profile", icon: "⚙️" }
  ];

  return (
    <>
      {/* Hero Background */}
      <div className="hero-background">
        <div className="hero-overlay"></div>
        <div className="hero-content">
          <h1 className={`hero-title ${fade ? "fade-in" : "fade-out"}`}>
            {title}
          </h1>
          <p className="hero-subtitle">
            Unlock the secrets of your subconscious
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <section className="services-section">
          <div className="container">
            <div className="section-header">
              <h2>What REMinder Does</h2>
              <p>Transform your dreams into meaningful insights</p>
            </div>
            
            <div className="services-grid">
              {features.slice(0, 3).map((feature, index) => (
                <div key={index} className="service-card">
                  <div className="service-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.subtitle}</p>
                  <ActionCard title={feature.title} subtitle={feature.subtitle} to={feature.to} icon={feature.icon} />
                </div>
              ))}
            </div>
            
            <div className="services-grid bottom-grid">
              {features.slice(3).map((feature, index) => (
                <div key={index + 3} className="service-card">
                  <div className="service-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.subtitle}</p>
                  <ActionCard title={feature.title} subtitle={feature.subtitle} to={feature.to} icon={feature.icon} />
                </div>
              ))}
            </div>
            
            <div className="all-services">
              <a href="/features" className="cta-button">
                View All Features
              </a>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
