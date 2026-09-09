from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event
from app.services.state_service import get_event_state
from app.services.prediction_service import predict_crowd_growth
from app.services.risk_factor_service import calculate_risk_factors
from app.services.risk_service import calculate_risk
from app.services.root_cause_service import identify_root_causes
from app.services.intervention_service import rank_interventions
from app.services.action_service import apply_intervention, list_applied_actions


router = APIRouter(
    prefix="/api/events",
    tags=["Interventions"],
)


class ApplyInterventionRequest(BaseModel):
    intervention_id: int
    approved_by: str | None = None
    action_details: str | None = None


@router.get("/{event_id}/interventions")
def get_interventions(
    event_id: int,
    db: Session = Depends(get_db),
):
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

    state = get_event_state(
        db=db,
        event_id=event_id,
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event state not available for event {event_id}",
        )

    # Find the most critical current zone.
    critical_zone = None
    critical_load = -1

    for zone_id, zone in state["zones"].items():
        capacity = zone.get("capacity") or 0
        current_count = zone.get("current_count") or 0

        if capacity <= 0:
            continue

        load = current_count / capacity

        if load > critical_load:
            critical_load = load
            critical_zone = zone_id

    if critical_zone is None:
        raise HTTPException(
            status_code=422,
            detail="No valid zone capacity/crowd data available",
        )

    zone = state["zones"][critical_zone]
    capacity = zone["capacity"]

    try:
        prediction = predict_crowd_growth(
            db=db,
            event_id=event_id,
            zone_id=int(critical_zone),
            capacity=capacity,
        )

        factors = calculate_risk_factors(
            state=state,
            zone_id=critical_zone,
            prediction=prediction,
        )

        risk = calculate_risk(**factors)

        root_causes = identify_root_causes(
            risk_result=risk,
            state=state,
            zone_id=critical_zone,
        )

        result = rank_interventions(
    db=db,
    event_id=event_id,
    risk_result=risk,
    root_causes=root_causes,
    state=state,
    zone_id=critical_zone,
    duration_minutes=30,
)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    return {
        "event_id": event_id,
        "event_name": event.event_name,
        "affected_zone": {
            "zone_id": int(critical_zone),
            "zone_name": zone["zone_name"],
        },
        "risk": {
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
        },
        "root_causes": root_causes["root_causes"],
        **result,
    }


@router.post("/{event_id}/interventions/apply")
def post_apply_intervention(
    event_id: int,
    body: ApplyInterventionRequest,
    db: Session = Depends(get_db),
):
    """
    Record that the organizer applied a recommended intervention.
    This is the "Apply" step in the product logic — it does not attempt to
    control any real transport/venue system, only logs the decision.
    """
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    try:
        result = apply_intervention(
            db=db,
            event_id=event_id,
            intervention_id=body.intervention_id,
            approved_by=body.approved_by,
            action_details=body.action_details,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return result


@router.get("/{event_id}/interventions/applied")
def get_applied_interventions(
    event_id: int,
    db: Session = Depends(get_db),
):
    """History of interventions the organizer has applied for this event."""
    return {"event_id": event_id, "applied_actions": list_applied_actions(db, event_id)}