// App.js
import React, { useEffect, useState, useRef } from "react";
import { Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";

import DreamAnalyzer from "./components/Dream_analyzer/DreamAnalyzer";
import DreamVisualizer from "./components/DreamVisualizer/DreamVisualizer";


import LandingPage from "./components/Landing/LandingPage";
import Login from "./components/Login_and_registration/login";
import Signup from "./components/Login_and_registration/Signup";
import ProtectedRoute from "./components/ProtectedRoute";

import Navbar from "./components/Common/Navbar/Navbar";
import Home from "./components/Home/HomePage";
import Footer from "./components/Common/Footer/footer";


import { authHeaders, logout } from "./auth";
import "./App.css";

function App() {
  const [dreams, setDreams] = useState([]);
  const listRef = useRef(null);

  const navigate = useNavigate();
  const location = useLocation();

  const standalonePages = ["/welcome", "/login", "/signup"];
  const isStandalone = standalonePages.includes(location.pathname);

  // Fetch dreams
  const fetchDreams = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_dreams", {
        method: "GET",
        headers: authHeaders(),
      });

      if (res.status === 401) {
        logout();
        return;
      }

      const data = await res.json();
      setDreams(data || []);
    } catch (err) {
      console.error("Error fetching dreams:", err);
    }
  };

  const addDream = async ({ title, content, mood }) => {
    try {
      const res = await fetch("http://127.0.0.1:5000/add_dream", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ title, content, mood }),
      });

      if (res.status === 401) {
        logout();
        throw new Error("Unauthorized");
      }

      const data = await res.json();

      await fetchDreams();
      scrollToBottom();

      return data;
    } catch (err) {
      console.error("Error adding dream:", err);
      throw err;
    }
  };

  const deleteDream = async (id) => {
    try {
      await fetch(`http://127.0.0.1:5000/delete_dream/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });

      await fetchDreams();
    } catch (err) {
      console.error("Error deleting dream:", err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    if (isStandalone) return;
    fetchDreams();
  }, [location.pathname]);

  const scrollToBottom = () => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  };

  return (
  <>
    {isStandalone ? (
      // Standalone pages (no navbar, no footer)
      <Routes>
        <Route path="/welcome" element={<LandingPage />} />
        <Route path="/login" element={<Login onLogin={() => navigate("/home")} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<Navigate to="/welcome" />} />
      </Routes>
    ) : (
      // Authenticated layout (one wrapper only!)
      <div className="App">       {/* THIS is the flex wrapper */}
        <Navbar />

        <div className="page-wrapper">
          <Routes>
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dream-analyzer"
              element={
                <ProtectedRoute>
                  <DreamAnalyzer
                    dreams={dreams}
                    onAdd={addDream}
                    onDelete={deleteDream}
                    listRef={listRef}
                  />
                </ProtectedRoute>
              }
            />

                            <Route 
                  path="/visualizer" 
                  element={
                    <ProtectedRoute>
                      <DreamVisualizer />
                    </ProtectedRoute>
                  }
                />


            <Route path="/" element={<Navigate to="/welcome" />} />
          </Routes>
        </div>

        <Footer />
      </div>
    )}
  </>
);

}

export default App;
