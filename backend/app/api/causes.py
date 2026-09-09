from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event, Zone
from app.services.state_service import get_event_state
from app.services.prediction_service import predict_crowd_growth
from app.services.risk_factor_service import calculate_risk_factors
from app.services.risk_service import calculate_risk
from app.services.root_cause_service import identify_root_causes


router = APIRouter(
    prefix="/api/events",
    tags=["Root Cause Analysis"],
)


@router.get("/{event_id}/causes/{entity_id}")
def get_root_causes(
    event_id: int,
    entity_id: int,
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
    # 2. Verify zone
    # ---------------------------------------------------------
    zone = (
        db.query(Zone)
        .filter(
            Zone.zone_id == entity_id,
            Zone.venue_id == event.venue_id,
        )
        .first()
    )

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail=f"Zone {entity_id} not found for event {event_id}",
        )

    if zone.capacity is None or zone.capacity <= 0:
        raise HTTPException(
            status_code=422,
            detail=f"Zone {entity_id} has no valid capacity",
        )

    # ---------------------------------------------------------
    # 3. Build current event state
    # ---------------------------------------------------------
    state = get_event_state(
        db=db,
        event_id=event_id,
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event state not available for event {event_id}",
        )

    zone_key = str(entity_id)

    if zone_key not in state["zones"]:
        raise HTTPException(
            status_code=422,
            detail=f"Current crowd state unavailable for zone {entity_id}",
        )

    # ---------------------------------------------------------
    # 4. Generate prediction
    # ---------------------------------------------------------
    try:
        prediction = predict_crowd_growth(
            db=db,
            event_id=event_id,
            zone_id=entity_id,
            capacity=zone.capacity,
        )

        # -----------------------------------------------------
        # 5. Generate risk factors
        # -----------------------------------------------------
        factors = calculate_risk_factors(
            state=state,
            zone_id=zone_key,
            prediction=prediction,
        )

        # -----------------------------------------------------
        # 6. Calculate risk
        # -----------------------------------------------------
        risk = calculate_risk(**factors)

        # -----------------------------------------------------
        # 7. Identify root causes
        # -----------------------------------------------------
        result = identify_root_causes(
            risk_result=risk,
            state=state,
            zone_id=zone_key,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    # ---------------------------------------------------------
    # 8. Return explainable result
    # ---------------------------------------------------------
    return {
        "event_id": event_id,
        "event_name": event.event_name,
        "zone_id": entity_id,
        "zone_name": zone.zone_name,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "root_causes": result["root_causes"],
    }