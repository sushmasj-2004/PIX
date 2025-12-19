import React, { useState, useEffect } from "react";
import axios from "axios";

export default function RegisterUser() {
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState({
    name: "",
    email: "",
    department: "",
    photo: null,
    password: "",
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/departments/")
      .then((res) => setDepartments(res.data))
      .catch(() => setDepartments([]));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.photo) {
      setMsg("Please fill all required fields");
      return;
    }

    const fd = new FormData();
    fd.append("name", form.name);
    fd.append("email", form.email);
    fd.append("department", form.department);
    fd.append("photo", form.photo);
    if (form.password) fd.append("password", form.password);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/register/",
        fd,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setMsg(res.data.message || "Registered Successfully");
      setForm({ name: "", email: "", department: "", photo: null, password: "" });
    } catch (err) {
      setMsg(err.response?.data?.error || "Registration Failed");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.heading}>Register Employee</h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Name</label>
            <input
              style={styles.input}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              style={styles.input}
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Department</label>
            <select
              style={styles.input}
              value={form.department}
              onChange={(e) =>
                setForm({ ...form, department: e.target.value })
              }
            >
              <option value="">-- None --</option>
              {departments.map((d) => (
                <option key={d.department_id} value={d.department_id}>
                  {d.department_name}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              value={form.password}
              onChange={(e) =>
                setForm({ ...form, password: e.target.value })
              }
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Photo</label>
            <input
              style={styles.fileInput}
              type="file"
              accept="image/*"
              onChange={(e) => setForm({ ...form, photo: e.target.files[0] })}
            />
          </div>

          <button type="submit" style={styles.button}>Register</button>
        </form>

        {msg && <p style={styles.message}>{msg}</p>}
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "90vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#fff8f0",
    padding: 20,
  },

  card: {
    background: "white",
    padding: "28px 32px",
    borderRadius: 14,
    width: "100%",
    maxWidth: 420,
    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
  },

  heading: {
    textAlign: "center",
    marginBottom: 20,
    color: "#333",
    fontFamily: "Segoe UI, sans-serif",
  },

  form: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },

  field: {
    display: "flex",
    flexDirection: "column",
  },

  label: {
    marginBottom: 6,
    fontWeight: 600,
    color: "#444",
  },

  input: {
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 15,
    outline: "none",
  },

  fileInput: {
    padding: "6px 0",
    fontSize: 15,
  },

  button: {
    marginTop: 10,
    padding: "12px 14px",
    background: "#ef6c6c",
    border: "none",
    color: "white",
    fontWeight: 600,
    borderRadius: 8,
    cursor: "pointer",
    fontSize: 15,
    boxShadow: "0 4px 12px rgba(0,0,0,0.12)",
    transition: "0.2s",
  },

  message: {
    marginTop: 16,
    textAlign: "center",
    fontWeight: 600,
    color: "#333",
  },
};
