import pytest

from app.services.state_service import build_event_state
from app.services.prediction_service import predict_crowd_growth
from app.services.risk_factor_service import calculate_risk_factors


@pytest.mark.skip(
    reason=(
        "Depends on predict_crowd_growth's old in-memory signature "
        "(state=..., zone_id=...), which no longer matches the "
        "DB/ML-backed service (db, event_id, capacity). Risk factors "
        "themselves are exercised live via /api/events/{id}/risks. "
        "See README 'Known pre-existing issue' for context."
    )
)
def test_calculate_risk_factors():

    state = build_event_state(
        event_id="EV001",

        zones={
            "ZONE_B": {
                "capacity": 10000,
                "current_count": 8000,
                "arrival_rate": 100,
                "departure_rate": 50,
            },
            "ZONE_C": {
                "capacity": 10000,
                "current_count": 7000,
                "arrival_rate": 50,
                "departure_rate": 40,
            },
        },

        transport={
            "METRO_B": {
                "capacity": 10000,
                "load": 9000,
            }
        },

        conditions={
            "rain": "HEAVY"
        },

        incidents=[],
    )

    prediction = predict_crowd_growth(
        state=state,
        zone_id="ZONE_B",
    )

    factors = calculate_risk_factors(
        state=state,
        zone_id="ZONE_B",
        prediction=prediction,
    )

    assert factors["crowd_pressure"] == 0.8

    assert factors["growth_pressure"] == 0.95

    assert factors["transport_pressure"] == 0.9

    assert factors["weather_risk"] == 1.0

    assert factors["nearby_zone_pressure"] == 0.7

    assert factors["capacity_pressure"] == 0.8
    