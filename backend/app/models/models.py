from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Numeric,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey("venues.venue_id"), nullable=False)
    event_name = Column(String(200), nullable=False)
    event_type = Column(String(100))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    expected_attendance = Column(Integer)
    name = Column(String(255))
    status = Column(String(50))
    scenario = Column(String(100))
    data_status = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)


class Venue(Base):
    __tablename__ = "venues"

    venue_id = Column(Integer, primary_key=True)
    venue_name = Column(String(150), nullable=False)
    address = Column(Text)
    capacity = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String(255))
    venue_type = Column(String(100))
    status = Column(String(50))
    data_status = Column(String(30))
    source = Column(String(255))


class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey("venues.venue_id"), nullable=False)
    zone_name = Column(String(150), nullable=False)
    capacity = Column(Integer)
    zone_type = Column(String(50))
    name = Column(String(255))
    parent_zone_id = Column(Integer)
    status = Column(String(50))
    data_status = Column(String(30))


class AccessPoint(Base):
    __tablename__ = "access_points"

    access_point_id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey("venues.venue_id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.zone_id"))
    access_name = Column(String(100), nullable=False)
    access_type = Column(String(30))
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String(255))
    capacity_per_minute = Column(Integer)
    status = Column(String(50))
    data_status = Column(String(30))


class CrowdState(Base):
    __tablename__ = "crowd_state"

    crowd_state_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.zone_id"), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    current_count = Column(Integer)
    inflow_rate = Column(Numeric(8, 2))
    outflow_rate = Column(Numeric(8, 2))
    density = Column(Numeric(8, 2))
    load_percentage = Column(Numeric(6, 2))
    timestamp = Column(DateTime)
    data_status = Column(String(30))


class TransportNode(Base):
    __tablename__ = "transport_nodes"

    transport_node_id = Column(Integer, primary_key=True)
    node_name = Column(String(150), nullable=False)
    node_type = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    capacity = Column(Integer)
    current_load = Column(Integer)
    load_percentage = Column(Numeric(5, 2))
    status = Column(String(50))
    data_status = Column(String(30))


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True)
    route_name = Column(String(150), nullable=False)
    route_type = Column(String(50))
    from_node_id = Column(Integer)
    to_node_id = Column(Integer)
    distance_km = Column(Float)
    estimated_time_minutes = Column(Integer)
    name = Column(String(255))
    capacity = Column(Integer)
    current_load = Column(Integer)
    travel_time_minutes = Column(Numeric)
    status = Column(String(50))
    data_status = Column(String(30))


class Accommodation(Base):
    __tablename__ = "accommodation"

    # Note: the PostGIS `location` geography column is intentionally not
    # mapped here — we read/write lat/lng directly instead.
    accommodation_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    accommodation_type = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    capacity = Column(Integer)
    data_source = Column(String(100))
    data_status = Column(String(30))
    available_units = Column(Integer)
    occupancy_percentage = Column(Numeric(5, 2))
    status = Column(String(50))


class Condition(Base):
    __tablename__ = "conditions"

    condition_id = Column(Integer, primary_key=True)
    event_id = Column(Integer)
    recorded_at = Column(DateTime, nullable=False)
    weather_type = Column(String(50))
    temperature = Column(Numeric(5, 2))
    rainfall_mm = Column(Numeric(6, 2))
    visibility_km = Column(Numeric(5, 2))
    severity = Column(String(30))
    timestamp = Column(DateTime)
    data_status = Column(String(30))


class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(Integer, primary_key=True)
    event_id = Column(Integer)
    incident_type = Column(String(100), nullable=False)
    description = Column(Text)
    severity = Column(String(30))
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    status = Column(String(50))
    reported_at = Column(DateTime)

class Intervention(Base):
    __tablename__ = "interventions"

    intervention_id = Column(Integer, primary_key=True)
    event_id = Column(
        Integer,
        ForeignKey("events.event_id"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False)

    intervention_name = Column(String(150), nullable=False)
    intervention_type = Column(String(100))
    description = Column(Text)
    target_area = Column(String(150))
    priority = Column(String(30))
    status = Column(String(30), default="PROPOSED")

    parameters = Column(Text)

    expected_risk_reduction = Column(Numeric(5, 2))
    expected_capacity_change = Column(Numeric(5, 2))
    people_benefited = Column(Integer)
    time_saved_minutes = Column(Integer)

    feasibility_score = Column(Numeric(5, 2))
    cost_score = Column(Numeric(5, 2))
    operational_impact = Column(Numeric(5, 2))
    overall_score = Column(Numeric(5, 2))
    rank = Column(Integer)

class AppliedAction(Base):
    __tablename__ = "applied_actions"

    action_id = Column(Integer, primary_key=True)

    event_id = Column(
        Integer,
        nullable=False,
    )

    intervention_id = Column(
        Integer,
        nullable=False,
    )

    applied_at = Column(
        DateTime,
        nullable=False,
    )

    approved_by = Column(String(150))

    action_status = Column(
        String(30),
        default="APPLIED",
    )

    action_details = Column(Text)

    resulting_state_version = Column(Integer)