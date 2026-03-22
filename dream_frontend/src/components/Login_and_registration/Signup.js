import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./auth.css";

function Signup() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const submitSignup = async (e) => {
    e.preventDefault();

    const res = await fetch("http://104.236.119.70:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, username, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Signup failed");
      return;
    }

    // 🔥 Handle verification ON vs OFF properly
    if (data.verification_required) {
      alert(
        `Account created! A verification link has been sent (check console for now) 📩\n\nEmail: ${email}`
      );
    } else {
      alert("Account created! You can now log in.");
    }

    // Redirect to login either way
    window.location.href = "/login";
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
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
          <Link to="/login">Already have an account? Sign in</Link>
        </div>
      </div>
    </div>
  );
}

export default Signup;
