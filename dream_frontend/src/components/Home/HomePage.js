import React, { useEffect, useState, useRef } from "react";
import "./home.css";
import ActionCard from "../Common/ActionCard/ActionCard";
import { useChatbot } from "../../context/ChatbotContext";

export default function Home() {
  const user = JSON.parse(localStorage.getItem("user"));
  const justLoggedIn = localStorage.getItem("justLoggedIn") === "true";

  const { toggleChat, setMessages } = useChatbot();

  const [title, setTitle] = useState("REMinder");
  const [fade, setFade] = useState(true);
  const timerRef = useRef(null);

  // Initial title setup
  useEffect(() => {
    if (justLoggedIn && user?.username) {
      setTitle(`Welcome Back ${user.username}`);
    }
  }, []);

  // Animation effect
  useEffect(() => {
    if (!justLoggedIn) return;

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(() => {
      setFade(false);

      setTimeout(() => {
        setTitle("REMinder");
        setFade(true);
        localStorage.setItem("justLoggedIn", "false");
      }, 600);
    }, 10000);

    return () => clearTimeout(timerRef.current);
  }, [justLoggedIn]);

  // 🔹 Chatbot starter
  const openDreamGuide = () => {
    toggleChat();
    setMessages([
      {
        role: "bot",
        text: "You can ask me anything about dreams — symbols, meanings, or patterns."
      }
    ]);
  };

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

          {/* 🔹 Step 6 Chatbot CTA */}
          <button className="cta-button" onClick={openDreamGuide}>
            Ask the Dream Guide
          </button>
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
                  <ActionCard {...feature} />
                </div>
              ))}
            </div>

            <div className="services-grid bottom-grid">
              {features.slice(3).map((feature, index) => (
                <div key={index + 3} className="service-card">
                  <div className="service-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.subtitle}</p>
                  <ActionCard {...feature} />
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
