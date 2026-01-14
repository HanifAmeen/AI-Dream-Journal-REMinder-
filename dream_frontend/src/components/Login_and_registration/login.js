import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./auth.css";

function Login() {
  const [mode, setMode] = useState("login"); // "login" or "signup"

  // Shared fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState(""); // signup only

  /* -----------------------
      LOGIN SUBMIT
  ------------------------ */
  const submitLogin = async (e) => {
    e.preventDefault();

    const res = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Login failed");
      return;
    }

    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));
    localStorage.setItem("justLoggedIn", "true");


    window.location.href = "/home";
  };

  /* -----------------------
      SIGNUP SUBMIT
  ------------------------ */
  const submitSignup = async (e) => {
    e.preventDefault();

    const res = await fetch("http://127.0.0.1:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, username, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || "Signup failed");
      return;
    }

    alert("Account created! You can now log in.");
    setMode("login");
  };

  return (
    <div className="auth-page">
      <div className={`auth-container form-wrapper ${mode === "signup" ? "morph-signup" : "morph-login"}`}>

        {/* ----------------------
             LOGIN FORM
        ------------------------ */}
        {mode === "login" && (
          <div className="form-content fade-slide-in">
            <h2>Login</h2>
            <form onSubmit={submitLogin} className="auth-form">
              <input
                type="email"
                placeholder="Email"
                value={email}
                required
                onChange={(e) => setEmail(e.target.value)}
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                required
                onChange={(e) => setPassword(e.target.value)}
              />

              <button type="submit">Login</button>
            </form>

            <div className="auth-footer">
              <button
                className="switch-btn"
                onClick={() => setMode("signup")}
              >
                Don’t have an account?<br />Create one
              </button>
            </div>
          </div>
        )}

        {/* ----------------------
             SIGNUP FORM
        ------------------------ */}
        {mode === "signup" && (
          <div className="form-content fade-slide-in">
            <h2>Signup</h2>
            <form onSubmit={submitSignup} className="auth-form">

             
              <input
                type="email"
                placeholder="Email"
                value={email}
                required
                onChange={(e) => setEmail(e.target.value)}
              />

            
              <input
                type="text"
                placeholder="Username"
                value={username}
                required
                onChange={(e) => setUsername(e.target.value)}
              />

            
              <input
                type="password"
                placeholder="Password"
                value={password}
                required
                onChange={(e) => setPassword(e.target.value)}
              />

              <button type="submit">Signup</button>
            </form>

            <div className="auth-footer">
              <button
                className="switch-btn"
                onClick={() => setMode("login")}
              >
                Already have an account?<br />Sign in
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default Login;
