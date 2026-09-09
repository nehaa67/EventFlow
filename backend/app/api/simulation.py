from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Event, Zone, Intervention

from app.services.state_service import get_event_state
from app.services.simulation_service import simulate_intervention


router = APIRouter(
    prefix="/api/events",
    tags=["Simulation"],
)


@router.post("/{event_id}/simulation")
def run_simulation(
    event_id: int,
    zone_id: int,
    intervention_id: int,
    duration_minutes: int = 30,
    db: Session = Depends(get_db),
):
    """
    Run a what-if simulation for an intervention.

    The simulation does NOT modify the real event state.

    It compares:
        - baseline without intervention
        - projected state with intervention
        - measurable impact
    """

    # -----------------------------------------------------
    # 1. Validate event
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 2. Validate zone belongs to event venue
    # -----------------------------------------------------

    zone = (
        db.query(Zone)
        .filter(
            Zone.zone_id == zone_id,
            Zone.venue_id == event.venue_id,
        )
        .first()
    )

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Zone {zone_id} not found "
                f"for event {event_id}"
            ),
        )

    if zone.capacity is None or zone.capacity <= 0:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Zone {zone_id} has no valid capacity"
            ),
        )

    # -----------------------------------------------------
    # 3. Validate intervention
    # -----------------------------------------------------

    intervention = (
        db.query(Intervention)
        .filter(
            Intervention.intervention_id
            == intervention_id,
            Intervention.event_id
            == event_id,
        )
        .first()
    )

    if intervention is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Intervention {intervention_id} "
                f"not found for event {event_id}"
            ),
        )

    # -----------------------------------------------------
    # 4. Validate duration
    # -----------------------------------------------------

    if duration_minutes <= 0:
        raise HTTPException(
            status_code=422,
            detail=(
                "duration_minutes must be "
                "greater than zero"
            ),
        )

    # -----------------------------------------------------
    # 5. Get current event state
    # -----------------------------------------------------

    state = get_event_state(
        db=db,
        event_id=event_id,
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Event state not available "
                f"for event {event_id}"
            ),
        )

    zone_key = str(zone_id)

    if zone_key not in state.get("zones", {}):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Current crowd state unavailable "
                f"for zone {zone_id}"
            ),
        )

    # -----------------------------------------------------
    # 6. Run what-if simulation
    # -----------------------------------------------------

    try:
        result = simulate_intervention(
            state=state,
            zone_id=zone_key,
            intervention_id=intervention_id,
            duration_minutes=duration_minutes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    # -----------------------------------------------------
    # 7. Return API response
    # -----------------------------------------------------

    return {
        "event_id": event_id,
        "event_name": event.event_name,

        "zone": {
            "zone_id": zone_id,
            "zone_name": zone.zone_name,
            "capacity": zone.capacity,
        },

        "intervention": {
            "intervention_id": (
                intervention.intervention_id
            ),
            "intervention_name": (
                intervention.intervention_name
            ),
            "intervention_type": (
                intervention.intervention_type
            ),
            "description": (
                intervention.description
            ),
            "target_area": (
                intervention.target_area
            ),
        },

        "simulation": result,
    }
