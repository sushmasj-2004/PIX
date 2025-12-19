import React from "react";
import { useNavigate } from "react-router-dom";

export default function UserDashboard() {
  const nav = useNavigate();

  return (
    <div style={container}>
      <div style={card}>
        <h2 style={title}>Welcome 👋</h2>
        <p style={subtitle}>Mark your attendance using face recognition.</p>

        <button style={primaryBtn} onClick={() => nav("/attendance")}>
          Open Webcam to Mark Attendance
        </button>
      </div>
    </div>
  );
}

const container = {
  minHeight: "100vh",
  background: "#f5f7fa",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  padding: 20,
};

const card = {
  background: "white",
  width: "360px",
  padding: "28px 24px",
  borderRadius: "14px",
  boxShadow: "0 4px 15px rgba(0,0,0,0.08)",
  textAlign: "center",
};

const title = {
  margin: 0,
  fontSize: "24px",
  fontWeight: "700",
  color: "#1f2937",
};

const subtitle = {
  marginTop: 8,
  marginBottom: 20,
  fontSize: "14px",
  color: "#6b7280",
};

const primaryBtn = {
  background: "#3b82f6",
  color: "white",
  padding: "10px 16px",
  borderRadius: "8px",
  border: "none",
  width: "100%",
  fontSize: "15px",
  cursor: "pointer",
  transition: "0.2s",
};

primaryBtn[":hover"] = {
  background: "#2563eb",
};
