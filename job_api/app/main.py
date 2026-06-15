from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS IMPORT
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, get_db
import app.models as models
from app.routes import job, user

# Reinitialize with standard, clean initialization parameters
app = FastAPI(title="Youth Job Opportunity API")

# =========================================================
# CORS MIDDLEWARE CLEARANCE (ALLOWS FRONTEND TO TALK TO BACKEND)
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your local index.html file to communicate
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Automatically generate database tables
Base.metadata.create_all(bind=engine)

# Include the routing blocks
app.include_router(job.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "Youth Job API is running smoothly"}

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "PostgreSQL is connected!"}
    except Exception as e:
        return {"status": "error", "message": f"Database failed: {str(e)}"}