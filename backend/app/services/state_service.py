from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    Event,
    Venue,
    Zone,
    AccessPoint,
    CrowdState,
    TransportNode,
    Route,
    Condition,
    Incident,
)


def build_event_state(
    event_id: int,
    zones: dict,
    transport: dict,
    conditions: dict,
    incidents: list | None = None,
    event: dict | None = None,
    venue: dict | None = None,
):
    """
    Build the unified EventFlow state.

    This is the common state format consumed by:
    prediction, risk, simulation, intervention and guidance services.
    """

    return {
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "event": event or {},
        "venue": venue or {},

        "zones": zones,
        "transport": transport,
        "conditions": conditions,
        "incidents": incidents or [],
    }


def get_event_state(db: Session, event_id: int):
    """
    Read the current event state from PostgreSQL and convert it
    into the common EventFlow state format.
    """

    # =========================================================
    # EVENT
    # =========================================================

    event_row = (
        db.query(Event)
        .filter(Event.event_id == event_id)
        .first()
    )

    if event_row is None:
        return None

    event_data = {
        "event_id": event_row.event_id,
        "event_name": event_row.event_name,
        "event_type": event_row.event_type,
        "start_time": (
            event_row.start_time.isoformat()
            if event_row.start_time
            else None
        ),
        "end_time": (
            event_row.end_time.isoformat()
            if event_row.end_time
            else None
        ),
        "expected_attendance": event_row.expected_attendance,
        "status": event_row.status,
        "scenario": event_row.scenario,
        "data_status": event_row.data_status,
    }

    # =========================================================
    # VENUE
    # =========================================================

    venue_row = (
        db.query(Venue)
        .filter(Venue.venue_id == event_row.venue_id)
        .first()
    )

    venue_data = {}

    if venue_row:
        venue_data = {
            "venue_id": venue_row.venue_id,
            "venue_name": venue_row.venue_name,
            "address": venue_row.address,
            "capacity": venue_row.capacity,
            "latitude": venue_row.latitude,
            "longitude": venue_row.longitude,
            "venue_type": venue_row.venue_type,
            "status": venue_row.status,
            "data_status": venue_row.data_status,
            "source": venue_row.source,
        }

    # =========================================================
    # ZONES
    #
    # Zones belong to the venue, not directly to the event.
    # =========================================================

    zone_rows = (
        db.query(Zone)
        .filter(Zone.venue_id == event_row.venue_id)
        .all()
    )

    zones = {}

    for zone in zone_rows:

        # Get latest crowd observation for THIS event + zone.
        latest_crowd = (
            db.query(CrowdState)
            .filter(
                CrowdState.event_id == event_id,
                CrowdState.zone_id == zone.zone_id,
            )
            .order_by(
                CrowdState.recorded_at.desc()
            )
            .first()
        )

        zone_data = {
            "zone_id": zone.zone_id,
            "zone_name": zone.zone_name,
            "capacity": zone.capacity,
            "zone_type": zone.zone_type,
            "status": zone.status,
            "data_status": zone.data_status,

            # Crowd values are populated when a current
            # observation exists.
            "current_count": None,
            "arrival_rate": None,
            "departure_rate": None,
            "density": None,
            "load_percentage": None,
            "recorded_at": None,
            "crowd_data_status": None,
        }

        if latest_crowd is not None:
            zone_data.update(
                {
                    "current_count": latest_crowd.current_count,
                    "arrival_rate": (
                        float(latest_crowd.inflow_rate)
                        if latest_crowd.inflow_rate is not None
                        else None
                    ),
                    "departure_rate": (
                        float(latest_crowd.outflow_rate)
                        if latest_crowd.outflow_rate is not None
                        else None
                    ),
                    "density": (
                        float(latest_crowd.density)
                        if latest_crowd.density is not None
                        else None
                    ),
                    "load_percentage": (
                        float(latest_crowd.load_percentage)
                        if latest_crowd.load_percentage is not None
                        else None
                    ),
                    "recorded_at": (
                        latest_crowd.recorded_at.isoformat()
                        if latest_crowd.recorded_at
                        else None
                    ),
                    "crowd_data_status": latest_crowd.data_status,
                }
            )

        zones[str(zone.zone_id)] = zone_data

    # =========================================================
    # ACCESS POINTS
    #
    # These are part of the venue digital twin.
    # =========================================================

    access_rows = (
        db.query(AccessPoint)
        .filter(
            AccessPoint.venue_id == event_row.venue_id
        )
        .all()
    )

    access_points = {}

    for access in access_rows:
        access_points[str(access.access_point_id)] = {
            "access_point_id": access.access_point_id,
            "zone_id": access.zone_id,
            "access_name": access.access_name,
            "access_type": access.access_type,
            "latitude": access.latitude,
            "longitude": access.longitude,
            "capacity_per_minute": access.capacity_per_minute,
            "status": access.status,
            "data_status": access.data_status,
        }

    # =========================================================
    # TRANSPORT
    #
    # Transport nodes are not event-linked in the DB.
    # Therefore we read the available transport network.
    # =========================================================

    transport_rows = (
        db.query(TransportNode)
        .all()
    )

    transport = {}

    for node in transport_rows:
        transport[str(node.transport_node_id)] = {
            "transport_node_id": node.transport_node_id,
            "node_name": node.node_name,
            "node_type": node.node_type,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "capacity": node.capacity,
            "current_load": node.current_load,
            "load_percentage": (
                float(node.load_percentage)
                if node.load_percentage is not None
                else None
            ),
            "status": node.status,
            "data_status": node.data_status,
        }

    # =========================================================
    # CONDITIONS
    # =========================================================

    condition = (
        db.query(Condition)
        .filter(Condition.event_id == event_id)
        .order_by(
            Condition.recorded_at.desc()
        )
        .first()
    )

    conditions = {}

    if condition:
        conditions = {
            "condition_id": condition.condition_id,
            "weather_type": condition.weather_type,
            "temperature": (
                float(condition.temperature)
                if condition.temperature is not None
                else None
            ),
            "rainfall_mm": (
                float(condition.rainfall_mm)
                if condition.rainfall_mm is not None
                else None
            ),
            "visibility_km": (
                float(condition.visibility_km)
                if condition.visibility_km is not None
                else None
            ),
            "severity": condition.severity,
            "recorded_at": (
                condition.recorded_at.isoformat()
                if condition.recorded_at
                else None
            ),
            "data_status": condition.data_status,
        }

    # =========================================================
    # INCIDENTS
    # =========================================================

    incident_rows = (
        db.query(Incident)
        .filter(
            Incident.event_id == event_id,
            Incident.status == "ACTIVE",
        )
        .all()
    )

    incidents = []

    for incident in incident_rows:
        incidents.append(
            {
                "incident_id": incident.incident_id,
                "incident_type": incident.incident_type,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "entity_type": incident.entity_type,
                "entity_id": incident.entity_id,
                "started_at": (
                    incident.started_at.isoformat()
                    if incident.started_at
                    else None
                ),
                "reported_at": (
                    incident.reported_at.isoformat()
                    if incident.reported_at
                    else None
                ),
            }
        )

    # =========================================================
    # FINAL UNIFIED STATE
    # =========================================================

    return build_event_state(
        event_id=event_row.event_id,
        event=event_data,
        venue=venue_data,
        zones=zones,
        transport=transport,
        conditions=conditions,
        incidents=incidents,
    )