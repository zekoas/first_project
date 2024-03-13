from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schema import Vote
from ..database import get_db
from ..auth2 import get_current_user
from .. import models

router = APIRouter(prefix="/votes", tags=["VOTES"])


@router.post("/")
async def vote(
    vote: Vote,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    got_vote = (
        db.query(models.Vote)
        .filter(models.Vote.user_id == user.id, models.Vote.post_id == vote.post_id)
        .first()
    )
    if not got_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POST WAS NOT FOUND"
        )
    if vote.dir == 1:
        if got_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already voted for this ",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=user.id)
        db.add(new_vote)
        db.commit()
        return "voted"
    else:
        if not got_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote dose not exist",
            )
        db.delete(got_vote)
        db.commit()
        return "the post was deleted"
