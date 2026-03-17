import React, { useState } from "react";
import "./Navbar.css";
import { Link, useNavigate } from "react-router-dom";

import Logo from "../../../Assets/Reminder_Logo1_Notext.png";
import Spector from "../../Home/homepage_assets/MK_flying.png";

function Navbar() {

  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const [runSpector, setRunSpector] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleLogoClick = () => {
    setRunSpector(true);

    setTimeout(() => {
      setRunSpector(false);
    }, 6000);


  };

  return (
    <header className="navbar-container">

      {/* Running Specter Animation */}
      {runSpector && (
        <img
          src={Spector}
          alt="running specter"
          className="spector-run"
        />
      )}

      <div className="navbar-left">
        <img
          src={Logo}
          alt="REMinder logo"
          className="navbar-logo"
          onClick={handleLogoClick}
        />

        <Link to="/home" className="nav-link">Home</Link>

        <p className="nav-username">
          {user?.username}
        </p>
      </div>

      <div className="navbar-right">
        <Link to="/tools" className="nav-link">Tools</Link>
        <Link to="/profile" className="nav-link">Profile</Link>
        <Link to="/about" className="nav-link">About us</Link>

        <button
          onClick={handleLogout}
          className="logout-button"
        >
          Logout
        </button>
      </div>

    </header>
  );
}

export default Navbar;