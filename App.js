import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Navbar";
import Login from "./Login";
import RegisterUser from "./RegisterUser";
import Attendance from "./Attendance";
import AdminDashboard from "./AdminDashboard";
import UserDashboard from "./UserDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navbar />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<RegisterUser />} />
        <Route path="/attendance" element={<Attendance />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/user-dashboard" element={<UserDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
