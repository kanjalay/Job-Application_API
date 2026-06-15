from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user") # 'admin', 'employer', or 'job_seeker'

    jobs = relationship("Job", back_populates="owner")


# CUSTOMIZED FOR YOUTH EMPLOYMENT LISTINGS
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(String, nullable=True)
    
    # Custom Youth-focused Fields
    job_type = Column(String, default="Full-time") # e.g., Internship, Part-time, Apprenticeship
    is_entry_level = Column(Boolean, default=True) # Great for young people with little experience
    offers_mentorship = Column(Boolean, default=False) # Adds extra value for youth development
    
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="jobs")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    seeker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, accepted, rejected

    # Optional Relationships (helps clean up queries later)
    job = relationship("Job")
    seeker = relationship("User")