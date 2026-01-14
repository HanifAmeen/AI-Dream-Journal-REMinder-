import React from "react";
import "./Navbar.css";
import { Link,useNavigate } from "react-router-dom";
import Logo from "../../../Assets/Reminder_Logo1_Notext.png";

function Navbar (){
const navigate = useNavigate();
const user = JSON.parse(localStorage.getItem("user"));

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };
  const navigateToHome = () => {
        navigate("/home");
  }

    return(
        <header className="navbar-container">
            <div className="navbar-left">
                <img src={Logo} alt="ReEMinder logo" className="navbar-logo"></img>
                  <Link to= "/home" className="nav-link" onClick={navigateToHome}>Home</Link>
                  <p className ="nav-username">{user?.username}</p>
            </div>
            <div className="navbar-right">
                  <Link to="/tools" className="nav-link">Tools</Link>
                  <Link to="/profile" className="nav-link">Profile</Link>
                  <Link to="/about" className="nav-link">About us</Link>
                  <button onClick={handleLogout} className="logout-button">Logout</button>
            </div>
           
        
             </header>

    
);

}





export default Navbar;



