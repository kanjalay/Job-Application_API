from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
import app.models as models
import app.schemas as schemas
from app.auth import get_current_user 

router = APIRouter(
    prefix="/jobs",
    tags=["Youth Job Listings"]
)

# 1. CREATE (Secured)
@router.post("/", response_model=schemas.JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_job = models.Job(**job.model_dump(), owner_id=current_user.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

# 2. READ ALL (Public)
@router.get("/", response_model=List[schemas.JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs

# 3. READ ONE (Public)
@router.get("/{id}", response_model=schemas.JobResponse)
def get_single_job(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job opportunity with id {id} was not found"
        )
    return job

# 4. UPDATE (Secured + Ownership Verification)
@router.put("/{id}", response_model=schemas.JobResponse)
def update_job(
    id: int, 
    updated_job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    job_query = db.query(models.Job).filter(models.Job.id == id)
    job = job_query.first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job opportunity with id {id} does not exist"
        )
        
    # Security Check: Ensure the logged-in user actually owns this job listing
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform requested action"
        )
        
    job_query.update(updated_job.model_dump(), synchronize_session=False)
    db.commit()
    return job_query.first()

# 5. DELETE (Secured + Ownership Verification)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    job_query = db.query(models.Job).filter(models.Job.id == id)
    job = job_query.first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job opportunity with id {id} does not exist"
        )
        
    # Security Check: Ensure the logged-in user actually owns this job listing
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform requested action"
        )
        
    job_query.delete(synchronize_session=False)
    db.commit()
    return {"detail": "Job post deleted successfully"}