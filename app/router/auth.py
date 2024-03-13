from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..schema import UserCreate, Token
from ..models import User
from ..utel import verify_password
from ..auth2 import create_access_token

router = APIRouter(tags=["AUTHENTICATION"])


@router.post("/login")
async def login(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_from_db = db.query(User).filter(User.email == user.username).first()
    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalied email or password"
        )
    if not verify_password(user.password, user_from_db.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalied email or password"
        )
    access_token = create_access_token(data={"user_id": user_from_db.id})
    return Token(access_token=access_token, token_type="bearer")
