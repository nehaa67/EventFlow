from sqlalchemy.orm import Session

from app.models import Accommodation


def _pressure_level(occupancy_percentage: float | None) -> str:
    """
    Classify accommodation pressure using the same SAFE / WARNING / HIGH /
    CRITICAL scale as crowd risk (risk_service.py), so organizers see one
    consistent meaning for "pressure" across zones, transport and lodging.
    """
    if occupancy_percentage is None:
        return "UNKNOWN"
    if occupancy_percentage <= 60:
        return "SAFE"
    if occupancy_percentage <= 80:
        return "WARNING"
    if occupancy_percentage <= 95:
        return "HIGH"
    return "CRITICAL"


def get_accommodation_overview(db: Session, limit_recommended: int = 3):
    """
    Read every accommodation zone in the destination and classify how much
    pressure it is under, so organizers can see where lodging is filling up
    and attendees can be steered toward comparatively less-pressured areas.

    Accommodation isn't tied to a single venue/event in the data model —
    it represents the wider destination (hotels, guesthouses, etc.) an
    event's visitors might use, which is what lets this work for any city
    or event, not just one stadium.
    """
    rows = (
        db.query(Accommodation)
        .order_by(Accommodation.occupancy_percentage.asc().nullslast())
        .all()
    )

    zones = []
    for row in rows:
        occupancy = (
            float(row.occupancy_percentage)
            if row.occupancy_percentage is not None
            else None
        )
        zones.append({
            "accommodation_id": row.accommodation_id,
            "name": row.name,
            "accommodation_type": row.accommodation_type,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "capacity": row.capacity,
            "available_units": row.available_units,
            "occupancy_percentage": occupancy,
            "pressure_level": _pressure_level(occupancy),
            "status": row.status,
        })

    # Recommend the least-pressured zones that still have open availability
    # and are actually operating — this is the "guide toward less-pressured
    # areas" behaviour called for in the team reference. A zone with a
    # couple of rooms left at 98% occupancy is technically "available" but
    # not a genuinely low-pressure option, so pressure level is checked too.
    candidates = [
        z for z in zones
        if (z["available_units"] or 0) > 0
        and z["status"] not in ("CLOSED", "INACTIVE")
        and z["pressure_level"] in ("SAFE", "WARNING")
    ]
    recommended = sorted(candidates, key=lambda z: z["occupancy_percentage"])[:limit_recommended]

    return {
        "accommodation": zones,
        "recommended": recommended,
    }
