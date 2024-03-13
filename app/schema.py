from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User_response(BaseModel):
    id: int
    email: EmailStr

    class config:
        orm_mode = True


class Post(BaseModel):
    title: str
    content: str | None = None
    published: bool = True


class Post_response(Post):
    created_at: datetime
    owner_id: int
    owner: User_response

    class config:
        orm_mode = True


class PostVote(BaseModel):
    post: Post_response
    vote_count: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None


class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
