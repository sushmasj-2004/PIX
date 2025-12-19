import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

export default function Attendance() {
  const webcamRef = useRef(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const captureAndSend = async () => {
    setLoading(true);
    setStatus("");
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      setStatus("Webcam not ready");
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem("token");
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await axios.post(
        "http://127.0.0.1:8000/api/start/",
        { image: imageSrc },
        { headers }
      );

      if (res.data.status === "success") {
        if (res.data.action === "login")
          setStatus(`🟢 Login recorded for ${res.data.name}`);
        else if (res.data.action === "logout")
          setStatus(
            `🟢 Logout recorded for ${res.data.name} — worked ${
              res.data.working_hours ?? "N/A"
            } hrs`
          );
        else setStatus("🟢 Attendance action completed");
      } else {
        setStatus("❌ " + (res.data.message || "Face not recognised"));
      }
    } catch (err) {
      setStatus("❌ Error contacting server");
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div style={styles.page}>
      <style>
        {`
          .card {
            background: #ffffff;
            padding: 32px;
            border-radius: 18px;
            max-width: 480px;
            width: 90%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            animation: fadeIn 0.4s ease;
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0); }
          }

          .title {
            font-size: 26px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
          }

          .cam-box {
            width: 340px;
            height: 260px;
            margin: 14px auto;
            border-radius: 14px;
            overflow: hidden;
            border: 3px solid #f3d7d7;
            background: #fafafa;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.06);
          }

          .btn {
            padding: 12px 26px;
            font-size: 17px;
            border: none;
            border-radius: 12px;
            background: #e85b81;
            color: white;
            cursor: pointer;
            transition: all 0.25s ease;
            font-weight: 500;
          }
          .btn:hover {
            background: #d6456a;
            transform: translateY(-2px);
          }
          .btn:disabled {
            background: #b9b9b9;
            cursor: not-allowed;
            transform: none;
          }

          .status {
            font-size: 16px;
            margin-top: 16px;
            color: #444;
            min-height: 30px;
          }
        `}
      </style>

      <div className="card">
        <h3 className="title">Check In</h3>

        <div className="cam-box">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            width="100%"
            height="100%"
          />
        </div>

        <button className="btn" onClick={captureAndSend} disabled={loading}>
          {loading ? "Processing..." : "Start"}
        </button>

        <div className="status">{status}</div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    background: "#fff6ec",
    padding: 20,
  },
};
