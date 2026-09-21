from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from database import *
from typing import Annotated
from models import *
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from decimal import Decimal

SECRET_KEY = "yq0Zr2XcU6V5VeRAKlkU7HozzdLdTdkH6I9zIn43Rok"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

class UserCreate(BaseModel):
    first_name: str
    username: str
    last_name: str
    password: str
    email: EmailStr
    address: str
    
    

class Token(BaseModel):
    access_token: str
    token_type: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)] 

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI where the login endpoint is for the Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: db_dependency, token: str = Depends(oauth2_scheme) ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/users")
async def read_users(db: db_dependency):
    return db.query(User).all()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: db_dependency):
    if user.username in [u.username for u in db.query(User).all()]:
        raise HTTPException(status_code=400, detail="Username already registered")
  
   
    myhashed_password = get_password_hash(user.password)

    db_user = User(username=user.username, hashed_password=myhashed_password, email=user.email, 
                   address=user.address, first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully"}




@router.post("/login", response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


