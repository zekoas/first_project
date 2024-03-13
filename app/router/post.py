from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schema import Post_response, Post, UserCreate, User_response, PostVote
from typing import List
from ..auth2 import get_current_user
from sqlalchemy import func


router = APIRouter(prefix="/posts", tags=["POSTS"])


@router.get("/", response_model=List[PostVote])
async def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    posts_with_votes = (
        db.query(models.Post, func.count(models.Vote.user_id).label("vote_count"))
        .outerjoin(models.Vote, models.Post.id == models.Vote.post_id)
        .filter(models.Post.title.contains(search))
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
        .all()
    )
    # Extract relevant information and create response objects
    post_responses = [
        {"post": post, "vote_count": vote_count}
        for post, vote_count in posts_with_votes
    ]

    return post_responses


@router.get("/{id}", response_model=PostVote)
async def post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post_vote = (
        db.query(models.Post, func.count(models.Vote.user_id).label("vote_count"))
        .outerjoin(models.Vote, models.Post.id == models.Vote.post_id)
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )
    if not post_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POST WAS NOT FOUND"
        )
    else:
        post, vote_count = post_vote
        return {"post": post, "vote_count": vote_count}


@router.post("/", response_model=Post_response)
async def create_post(
    post: Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    posts = models.Post(owner_id=current_user.id, **post.dict())
    db.add(posts)
    db.commit()
    db.refresh(posts)
    return posts


@router.put("/{id}")
async def update_post(
    id: int,
    post: Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    old_post = db.query(models.Post).filter(models.Post.id == id).first()
    if not old_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POST WAS NOT FOUND"
        )
    if old_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CAN NOT PERFORM THIS ACTION"
        )
    # Update the attributes of old_post with the values from the request
    for key, value in post.dict().items():
        setattr(old_post, key, value)
    db.commit()
    return "Post updated"


@router.delete("/{id}")
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POST WAS NOT FOUND"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CAN NOT PERFORM THIS ACTION"
        )
    db.delete(post)
    db.commit()
    return "post was deleted"
