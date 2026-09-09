from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event, Zone
from app.services.state_service import get_event_state
from app.services.prediction_service import predict_crowd_growth
from app.services.risk_factor_service import calculate_risk_factors
from app.services.risk_service import calculate_risk


router = APIRouter(
    prefix="/api/events",
    tags=["Risk"],
)


@router.get("/{event_id}/risks")
def get_event_risks(
    event_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Verify event
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Build current DB-backed event state
    # ---------------------------------------------------------
    state = get_event_state(db, event_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event state not available for event {event_id}",
        )

    # ---------------------------------------------------------
    # 3. Get all zones belonging to the event venue
    # ---------------------------------------------------------
    zones = (
        db.query(Zone)
        .filter(Zone.venue_id == event.venue_id)
        .order_by(Zone.zone_id)
        .all()
    )

    results = []
    critical_zones = []

    # ---------------------------------------------------------
    # 4. Calculate prediction → factors → risk for each zone
    # ---------------------------------------------------------
    for zone in zones:

        if zone.capacity is None or zone.capacity <= 0:
            results.append({
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "status": "INSUFFICIENT_DATA",
                "reason": "Zone capacity is unavailable",
            })
            continue

        zone_key = str(zone.zone_id)

        if zone_key not in state["zones"]:
            results.append({
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "status": "INSUFFICIENT_DATA",
                "reason": "Current crowd state is unavailable",
            })
            continue

        try:
            # ML prediction
            prediction = predict_crowd_growth(
                db=db,
                event_id=event_id,
                zone_id=zone.zone_id,
                capacity=zone.capacity,
            )

            # Six normalized risk factors
            factors = calculate_risk_factors(
                state=state,
                zone_id=zone_key,
                prediction=prediction,
            )

            # Deterministic weighted risk engine
            risk = calculate_risk(
                **factors
            )

            result = {
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "current_count": prediction["current_count"],
                "capacity": prediction["capacity"],
                "current_load_percentage": prediction[
                    "current_load_percentage"
                ],
                "prediction": prediction,
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"],
                "reason_signals": risk["reason_signals"],
                "factors": risk["factors"],
                "hotspot": prediction["hotspot"],
            }

            results.append(result)

            if risk["risk_level"] in {"HIGH", "CRITICAL"}:
                critical_zones.append({
                    "zone_id": zone.zone_id,
                    "zone_name": zone.zone_name,
                    "risk_score": risk["risk_score"],
                    "risk_level": risk["risk_level"],
                })

        except ValueError as exc:
            results.append({
                "zone_id": zone.zone_id,
                "zone_name": zone.zone_name,
                "status": "INSUFFICIENT_DATA",
                "reason": str(exc),
            })

    # ---------------------------------------------------------
    # 5. Event-level summary
    # ---------------------------------------------------------
    if critical_zones:
        event_risk_score = max(
            item["risk_score"]
            for item in critical_zones
        )

        event_risk_level = max(
            critical_zones,
            key=lambda item: item["risk_score"],
        )["risk_level"]
    else:
        valid_scores = [
            item["risk_score"]
            for item in results
            if "risk_score" in item
        ]

        event_risk_score = (
            max(valid_scores)
            if valid_scores
            else 0.0
        )

        if event_risk_score <= 30:
            event_risk_level = "SAFE"
        elif event_risk_score <= 60:
            event_risk_level = "WARNING"
        elif event_risk_score <= 80:
            event_risk_level = "HIGH"
        else:
            event_risk_level = "CRITICAL"

    return {
        "event_id": event_id,
        "event_name": event.event_name,
        "event_risk_score": event_risk_score,
        "event_risk_level": event_risk_level,
        "zones": results,
        "high_risk_zones": critical_zones,
        "total_zones": len(zones),
    }