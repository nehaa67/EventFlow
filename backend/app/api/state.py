from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.state_service import get_event_state

router = APIRouter(
    prefix="/api/events",
    tags=["Event State"],
)


@router.get("/{event_id}/state")
def read_event_state(
    event_id: int,
    db: Session = Depends(get_db),
):
    state = get_event_state(db, event_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found",
        )

    return state