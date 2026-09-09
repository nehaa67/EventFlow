from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event, Zone
from app.services.prediction_service import predict_crowd_growth


router = APIRouter(
    prefix="/api/events",
    tags=["Predictions"],
)


@router.get("/{event_id}/predictions")
def get_event_predictions(
    event_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------------
    # Verify event
    # ---------------------------------------------------------------

    event = (
        db.query(Event)
        .filter(Event.event_id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found",
        )

    # ---------------------------------------------------------------
    # Get zones belonging to the event's venue
    # ---------------------------------------------------------------

    zones = (
        db.query(Zone)
        .filter(Zone.venue_id == event.venue_id)
        .order_by(Zone.zone_id)
        .all()
    )

    results = []
    hotspots = []

    for zone in zones:

        if zone.capacity is None or zone.capacity <= 0:
            results.append({
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "status": "INSUFFICIENT_DATA",
                "reason": "Zone capacity is unavailable",
            })
            continue

        try:
            prediction = predict_crowd_growth(
                db=db,
                event_id=event_id,
                zone_id=zone.zone_id,
                capacity=zone.capacity,
            )

            prediction["zone_name"] = zone.zone_name

            results.append(prediction)

            if prediction["hotspot"]:
                hotspots.append({
                    "zone_id": zone.zone_id,
                    "zone_name": zone.zone_name,
                    "max_predicted_load_percentage": (
                        prediction[
                            "max_predicted_load_percentage"
                        ]
                    ),
                    "breach_eta": prediction["breach_eta"],
                })

        except ValueError as exc:

            results.append({
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "status": "INSUFFICIENT_DATA",
                "reason": str(exc),
            })

    # ---------------------------------------------------------------
    # Final API response
    # ---------------------------------------------------------------

    return {
        "event_id": event_id,
        "event_name": event.event_name,
        "zones": results,
        "hotspots": hotspots,
        "total_zones": len(zones),
        "prediction_horizons": [10, 20, 30],
    }