# Face Attendance System (Django + React + DeepFace)

A full-stack face-recognition attendance system built using:
- **Django REST Framework** (Backend)
- **React JS** (Frontend)
- **DeepFace + OpenCV** (Face Recognition)
- **SQLite / PostgreSQL** (Database)

## 📌 Features

### 👨‍💼 User Management
- Register user with name, email, department, photo  
- Store user data in Django Models  
- Admin can view/manage users via `/admin/`  

### 👁️ Face Recognition
- Real-time webcam capture from React  
- DeepFace match on Django side  
- Automatic login/logout logic:
  - First attendance of the day → **login_time**
  - Later attempts → **logout_time** update  
  - Only one record per day  

### 🕒 Attendance Tracking
- Tracks:
  - Date
  - Login time
  - Logout time
  - Optional: working hours  
- Data stored in `Attendance` table  

### 🧭 Frontend Navigation
- Dashboard
- Register User
- Mark Attendance
- Logout  

---

## 📁 Folder Structure

project-root/
│
├── backend/
│ ├── faceapp/
│ ├── faceapp/settings.py
│ ├── faceapp/urls.py
│ ├── manage.py
│
├── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│
├── README.md
├── .gitignore


---

## 🚀 Setup Instructions

### 1️⃣ Backend Setup (Django)

cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Backend runs at:
http://127.0.0.1:8000/

Frontend Setup (React)
cd frontend
npm install
npm start

Frontend runs at:
http://localhost:3000/

🔗 API Endpoints
| Method | Endpoint                | Description        |
| ------ | ----------------------- | ------------------ |
| POST   | `/api/register/`        | Register user      |
| POST   | `/api/mark-attendance/` | Login/Logout logic |
| GET    | `/api/departments/`     | Fetch departments  |
| POST   | `/api/logout/`          | Logout user        |
| POST   | `/api/login/`           | Login user         |

🧠 Attendance Logic

If user has no attendance record for today → create with login_time

If record already exists → update logout_time

Never create multiple records for same user/day

👨‍💻 Admin Panel

Visit:

http://127.0.0.1:8000/admin/


Use superuser credentials.

🛠 Technologies Used

Python 3

Django REST Framework

DeepFace

OpenCV

React JS

Axios

HTML/CSS/JS

✔️ Author

Project by Sushma J (ECE 4th Year)

End of README

---

# ✅ **.gitignore (For Django + React Project)**  
Paste this into your project root as `.gitignore`:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.env
.env
venv/
env/
build/
dist/
*.sqlite3

# Django
/media/
staticfiles/
static/
*.log

# VS Code
.vscode/

# Virtual environments
venv/
env/

# React
node_modules/
build/
.cache/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS Files
.DS_Store
Thumbs.db

# Hidden files
*.bak
*.tmp

# DeepFace cache
deepface_cache/

# Uploads
uploads/
photos/
