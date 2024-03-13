from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from .. import models
from ..utel import get_password_hash, verify_password
from ..schema import Post_response, Post, UserCreate, User_response
from ..database import get_db

router = APIRouter(prefix="/user", tags=["USERS"])


@router.get("/{id}", response_model=User_response)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER WAS NOT FOUND"
        )
    else:
        return user


@router.post("/", response_model=User_response)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed = get_password_hash(user.password)
    user.password = hashed
    create_users = models.User(**user.dict())
    db.add(create_users)
    db.commit()
    db.refresh(create_users)
    return create_users
