from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AppliedAction, Intervention


def apply_intervention(
    db: Session,
    event_id: int,
    intervention_id: int,
    approved_by: str | None = None,
    action_details: str | None = None,
):
    """
    Record that an organizer accepted/applied a recommended intervention.

    This is the "Apply" stage of the product logic: Monitor -> Predict ->
    Detect Risk -> Explain -> Recommend -> Simulate -> **Apply** -> Guide.
    It's a lightweight audit log (applied_actions), not a claim of real
    control over transport/venue systems — in line with the MVP boundary
    that real-world control is out of scope for the demo.
    """
    intervention = (
        db.query(Intervention)
        .filter(
            Intervention.intervention_id == intervention_id,
            Intervention.event_id == event_id,
        )
        .first()
    )

    if intervention is None:
        raise ValueError(
            f"Intervention {intervention_id} not found for event {event_id}"
        )

    action = AppliedAction(
        event_id=event_id,
        intervention_id=intervention_id,
        applied_at=datetime.now(timezone.utc),
        approved_by=approved_by,
        action_status="APPLIED",
        action_details=action_details,
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return {
        "action_id": action.action_id,
        "event_id": action.event_id,
        "intervention_id": action.intervention_id,
        "intervention_name": intervention.intervention_name,
        "applied_at": action.applied_at.isoformat(),
        "approved_by": action.approved_by,
        "action_status": action.action_status,
    }


def list_applied_actions(db: Session, event_id: int):
    rows = (
        db.query(AppliedAction)
        .filter(AppliedAction.event_id == event_id)
        .order_by(AppliedAction.applied_at.desc())
        .all()
    )
    return [
        {
            "action_id": row.action_id,
            "event_id": row.event_id,
            "intervention_id": row.intervention_id,
            "applied_at": row.applied_at.isoformat() if row.applied_at else None,
            "approved_by": row.approved_by,
            "action_status": row.action_status,
        }
        for row in rows
    ]
