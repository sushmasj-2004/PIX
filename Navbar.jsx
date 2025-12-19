import React from "react";
import "./Navbar.css";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

  const handleMarkAttendance = () => {
    navigate("/attendance");
  };

  return (
    <div className="navbar-container">
      <nav className="navbar">
        <div className="navbar-title">PIX Face Attendance</div>

        <div className="navbar-buttons">
          <button className="btn login-btn" onClick={handleLogin}>
            Login
          </button>
          <button className="btn attendance-btn" onClick={handleMarkAttendance}>
            Face Check
          </button>
        </div>
      </nav>
    </div>
  );
}
