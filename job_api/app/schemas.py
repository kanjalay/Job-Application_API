from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# =========================================================
#                 USER / AUTHENTICATION SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True


# =========================================================
#                   YOUTH JOB LISTING SCHEMAS
# =========================================================

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: int
    job_type: str 
    is_entry_level: bool = True
    offers_mentorship: bool = False

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: int
    job_type: str
    is_entry_level: bool
    offers_mentorship: bool
    is_active: bool
    owner_id: int  
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True

# =========================================================
#                JOB APPLICATION SCHEMAS
# =========================================================

class ApplicationCreate(BaseModel):
    message: str # Catches the pitch text from the frontend modal

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    seeker_id: int
    message: str
    status: str # "pending", "accepted", "rejected"
    
    class Config:
        from_attributes = True