import React, { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";  // ✅ ADDED THIS IMPORT
import "./home.css";
import { useChatbot } from "../../context/ChatbotContext";

// 🔹 Import feature images
import analyzerImg from "./homepage_assets/dream_analyzer.png";
import visualizerImg from "./homepage_assets/dream_visualizer.png";
import profileImg from "./homepage_assets/moonknightprofile.png";

export default function Home() {
  const user = JSON.parse(localStorage.getItem("user"));
  const justLoggedIn = localStorage.getItem("justLoggedIn") === "true";

  const { toggleChat, setMessages } = useChatbot();

  const [title, setTitle] = useState("REMinder");
  const [fade, setFade] = useState(true);
  const timerRef = useRef(null);

  useEffect(() => {
    if (justLoggedIn && user?.username) {
      setTitle(`Welcome Back ${user.username}`);
    }
  }, []);

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

  const openDreamGuide = () => {
    toggleChat();
    setMessages([
      {
        role: "bot",
        text: "You can ask me anything about dreams — symbols, meanings, or patterns."
      }
    ]);
  };

  // 🔹 Only the 3 cards you want
  const features = [
    {
      title: "AI Analyzer",
      subtitle: "Unlock the meaning of your dreams",
      to: "/dream-analyzer",
      image: analyzerImg
    },
    {
      title: "Visualizer",
      subtitle: "See your dream texts come alive",
      to: "/visualizer",
      image: visualizerImg
    },
    {
      title: "Profile",
      subtitle: "Manage your settings",
      to: "/profile",
      image: profileImg
    }
  ];

  return (
    <>
      {/* Hero Background */}
      <div className="hero-background">
        <div className="dream-symbols">
          <span className="symbol moon" style={{ "--i": 1 }}>🌙</span>
          <span className="symbol eye" style={{ "--i": 2 }}>🌙</span>
          <span className="symbol key" style={{ "--i": 3 }}>🗝️</span>
          <span className="symbol door" style={{ "--i": 4 }}>🚪</span>
          <span className="symbol stairs" style={{ "--i": 5 }}>🪜</span>
          <span className="symbol water" style={{ "--i": 6 }}>💧</span>
          <span className="symbol mask" style={{ "--i": 7 }}>🎭</span>
        </div>

        <div className="hero-overlay"></div>

        <div className="hero-content">
          <h1 className={`hero-title ${fade ? "fade-in" : "fade-out"}`}>
            {title}
          </h1>

          <p className="hero-subtitle">
            Unlock the secrets of your subconscious
          </p>

          <button className="cta-button" onClick={openDreamGuide}>
            Ask the Dream Guide
          </button>
        </div>
      </div>

      {/* Feature Section */}
      <div className="main-content">
        <section className="services-section">
          <div className="container">
            <div className="section-header">
              <h2>Explore REMinder</h2>
              <p>Analyze, visualize, and understand your dreams</p>
            </div>

            <div className="services-grid">
              {features.map((feature, index) => (
                <div key={index} className="service-item">
                  {/* ✅ FIXED: Direct image + Link navigation */}
                  <Link to={feature.to} className="service-card-link">
                    <div 
                      className="service-card-image-wrapper" 
                      style={{ "--i": index }}
                    >
                      <img 
                        src={feature.image} 
                        alt={feature.title}
                        className="service-card-image"
                      />
                    </div>
                  </Link>
                  <h3 className="service-title">{feature.title}</h3>
                  <p className="service-subtitle">{feature.subtitle}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
