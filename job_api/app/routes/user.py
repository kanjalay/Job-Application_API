from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
import app.models as models
import app.schemas as schemas
import app.auth as auth
from app.auth import get_current_user # Our secure token gatekeeper



router = APIRouter(

    prefix="/auth",

    tags=["Authentication & Users"]

)



# 1. REGISTER AN ACCOUNT (Keep this!)

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)

def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if user already exists

    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()

    if existing_user:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="A user with this email already exists."

        )

   

    # Hash the password cleanly using direct bcrypt

    hashed_pwd = auth.hash_password(user_in.password)

   

    # Save to PostgreSQL

    new_user = models.User(

        username=user_in.username,

        email=user_in.email,

        password=hashed_pwd,

        role=user_in.role

    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user





# 2. LOG IN / GENERATE TOKEN (Keep this!)

@router.post("/login")

def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Find user by username

    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Incorrect username or password"

        )

   

    # Verify password hash

    if not auth.verify_password(form_data.password, user.password):

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Incorrect username or password"

        )

   

    # Create the secure digital passport token

    access_token = auth.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}





# 3. READ MY PROFILE (New - Appended!)

@router.get("/me", response_model=schemas.UserResponse)

def get_my_profile(current_user: models.User = Depends(get_current_user)):

    """

    Takes your active token, looks up who you are automatically,

    and returns your exact user credentials securely.

    """

    return current_user





# 4. UPDATE MY PROFILE (New - Appended!)

@router.put("/me", response_model=schemas.UserResponse)

def update_my_profile(

    profile_updates: schemas.UserUpdate,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)

):

    """

    Allows a logged in user to safely change their email address in PostgreSQL.

    """

    user_query = db.query(models.User).filter(models.User.id == current_user.id)

    update_data = profile_updates.model_dump(exclude_unset=True)

   

    if not update_data:

        raise HTTPException(status_code=400, detail="No update data provided")

       

    user_query.update(update_data, synchronize_session=False)

    db.commit()

   

    return user_query.first() 

