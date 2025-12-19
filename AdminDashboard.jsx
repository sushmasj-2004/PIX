import React from "react";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const nav = useNavigate();

  return (
    <div style={styles.container}>
      <style>
        {`
          .card {
            background: #ffffff;
            padding: 30px;
            border-radius: 18px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.08);
            max-width: 420px;
            margin: auto;
            text-align: center;
          }
          .title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 25px;
            color: #2d3748;
            font-family: 'Segoe UI', sans-serif;
          }
          .btn-box {
            display: flex;
            flex-direction: column;
            gap: 14px;
          }
          .btn {
            padding: 14px;
            font-size: 16px;
            border: none;
            background: #4a90e2;
            color: white;
            border-radius: 12px;
            cursor: pointer;
            transition: 0.25s ease;
            font-family: 'Segoe UI', sans-serif;
          }
          .btn:hover {
            background: #357ABD;
            transform: translateY(-2px);
          }
        `}
      </style>

      <div className="card">
        <h2 className="title">Admin Dashboard</h2>

        <div className="btn-box">
          <button className="btn" onClick={() => nav("/register")}>
            Register Employee
          </button>

          <button className="btn" onClick={() => nav("/attendance")}>
            Mark Attendance
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    background: "#f3f6fa",
  },
};
