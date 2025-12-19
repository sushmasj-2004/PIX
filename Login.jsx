import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Login() {
  const nav = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPass] = useState("");
  const [error, setError] = useState("");

  const loginUser = async () => {
    setError("");

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/login/",
        { email:email, password:password },
        { withCredentials: true }
      );

      if (res.data.status === "success") {
        try {
          const userObj = {
            user_id: res.data.user_id,
            is_admin: res.data.is_admin,
            name: res.data.name,
            email: res.data.email,
          };
          localStorage.setItem("user", JSON.stringify(userObj));
          if (res.data.token) {
            localStorage.setItem("token", res.data.token);
          }
        } catch (e) {
          console.warn("Could not save user/token to localStorage", e);
        }

        if (res.data.is_admin) nav("/admin-dashboard");
        else nav("/user-dashboard");
      } else {
        setError("Invalid email or password");
      }
    } catch (err) {
      setError("Login failed");
    }
  };

  return (
    <div style={styles.page}>
      <style>
        {`
          .login-card {
            background: #ffffff;
            padding: 34px;
            border-radius: 18px;
            width: 380px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            font-family: 'Segoe UI', sans-serif;
            animation: fadeIn 0.4s ease;
            text-align: center;
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0); }
          }

          .login-title {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 25px;
            color: #2d3748;
          }

          .login-input {
            width: 100%;
            padding: 12px 14px;
            margin-bottom: 16px;
            border-radius: 10px;
            border: 1px solid #d9d9d9;
            font-size: 16px;
            background: #fafafa;
            transition: all 0.25s ease;
          }
          .login-input:focus {
            outline: none;
            border-color: #e85b81;
            box-shadow: 0 0 0 3px rgba(232,91,129,0.2);
            background: #fff;
          }

          .login-btn {
            margin-top: 8px;
            width: 100%;
            padding: 12px 0;
            background: #e85b81;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 17px;
            cursor: pointer;
            transition: all 0.25s ease;
            font-weight: 500;
          }
          .login-btn:hover {
            background: #d6456a;
            transform: translateY(-2px);
          }

          .error-text {
            margin-top: 12px;
            font-size: 15px;
            color: #cc0000;
            min-height: 20px;
          }
        `}
      </style>

      <div className="login-card">
        <h2 className="login-title">Welcome Back 👋</h2>

        <input
          className="login-input"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="login-input"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPass(e.target.value)}
        />

        <button className="login-btn" onClick={loginUser}>
          Login
        </button>

        {error && <p className="error-text">{error}</p>}
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
  },
};
