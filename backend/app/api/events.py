from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event, Venue

router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


@router.get("")
def list_events(db: Session = Depends(get_db)):
    """
    List every event, with its venue name, so the frontend can offer a
    proper picker instead of asking the user to type a numeric event ID.
    Intentionally lightweight — just enough to populate a dropdown.
    """
    rows = (
        db.query(Event, Venue.venue_name)
        .join(Venue, Venue.venue_id == Event.venue_id, isouter=True)
        .order_by(Event.event_id)
        .all()
    )

    return {
        "events": [
            {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "venue_name": venue_name,
                "status": event.status,
                "scenario": event.scenario,
            }
            for event, venue_name in rows
        ]
    }
