import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-icons">
        <a href="#" aria-label="Facebook"><i className="fab fa-facebook-f"></i></a>
        <a href="#" aria-label="Instagram"><i className="fab fa-instagram"></i></a>
        <a href="#" aria-label="Twitter"><i className="fab fa-twitter"></i></a>
        <a href="#" aria-label="Google"><i className="fab fa-google"></i></a>
        <a href="#" aria-label="YouTube"><i className="fab fa-youtube"></i></a>
      </div>

      <div className="footer-links">
        <a href="/">Home</a>
        <a href="/news">News</a>
        <a href="/about">About</a>
        <a href="/contact">Contact Us</a>
        <a href="/team">Our Team</a>
      </div>

      <p className="footer-copy">
        © {new Date().getFullYear()} REMinder · Designed by Hanif
      </p>
    </footer>
  );
};

export default Footer;
