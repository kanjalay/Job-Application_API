# Job-Application_API
Practicing Swagger UI and using REST and Fast API Architecture
# SL Mamekoka – Youth Job Opportunity API

📌 Overview
SL Mamekoka is a FastAPI-based platform designed to connect Sierra Leonean youth with job opportunities. The system allows employers to post jobs and job seekers to discover and apply for them.

This project aligns with **SDG 8: Decent Work and Economic Growth**, promoting youth employment and digital participation.

🚀 Features

- User Registration & Login (JWT Authentication)
- Role-based access (Employer / Job Seeker)
- Job CRUD Operations
- Secure API endpoints
- PostgreSQL database integration
- Interactive frontend (python streamlite )

 🛠 Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: OAuth2 + JWT
- Frontend: python streamlit

📂 Project Structure
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── routes/
│ ├── user.py
│ ├── job.py


🔐 Authentication

This API uses **OAuth2 with JWT tokens**.

### Login


📡 API Endpoints

### 👤 Users
| Method | Endpoint | Description |
|-------|---------|------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login user |
| GET | /auth/me | Get current user |
| PUT | /auth/me | Update profile |


### 💼 Jobs
| Method | Endpoint | Description |
|-------|---------|------------|
| GET | /jobs/ | Get all jobs |
| GET | /jobs/{id} | Get single job |
| POST | /jobs/ | Create job (Auth required) |
| PUT | /jobs/{id} | Update job (Owner only) |
| DELETE | /jobs/{id} | Delete job (Owner only) |


🧪 API Documentation

FastAPI automatically provides:

- Swagger UI → http://127.0.0.1:8000/docs  
- ReDoc → http://127.0.0.1:8000/redoc  


⚙️ Setup Instructions
1. Clone Repository
```bash
git clone https://github.com/your-repo/mamekoka.git
cd mamekoka

python -m venv venv
source venv/bin/activate   # or Windows: venv\Scripts\activate

pip install -r requirements.txt

DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key

uvicorn app.main:app --reload

