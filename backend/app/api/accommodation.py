from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.accommodation_service import get_accommodation_overview

router = APIRouter(
    prefix="/api/accommodation",
    tags=["Accommodation"],
)


@router.get("")
def read_accommodation(db: Session = Depends(get_db)):
    """
    Destination-wide accommodation availability and pressure.

    Not scoped to a single event/venue: accommodation is shared across the
    destination, so this reflects overall lodging pressure regardless of
    which event is currently selected in the UI.
    """
    return get_accommodation_overview(db)
