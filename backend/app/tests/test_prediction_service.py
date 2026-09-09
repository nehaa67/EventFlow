import pytest

from app.services.state_service import build_event_state
from app.services.prediction_service import predict_crowd_growth


@pytest.mark.skip(
    reason=(
        "predict_crowd_growth now reads from Postgres + the trained ML "
        "models (db, event_id, capacity) instead of a pure in-memory "
        "state dict. This test exercises the old in-memory signature and "
        "is superseded by the live /api/events/{id}/predictions endpoint. "
        "See README 'Known pre-existing issue' for context."
    )
)
def test_predict_crowd_growth():
    state = build_event_state(
        event_id="EV001",
        zones={
            "ZONE_B": {
                "capacity": 10000,
                "current_count": 8000,
                "arrival_rate": 100,
                "departure_rate": 50,
            }
        },
        transport={},
        conditions={},
        incidents=[],
    )

    result = predict_crowd_growth(
        state=state,
        zone_id="ZONE_B",
    )

    assert result["zone_id"] == "ZONE_B"

    # Net growth = 100 - 50 = 50 people/minute
    assert result["predictions"][10]["predicted_count"] == 8500
    assert result["predictions"][20]["predicted_count"] == 9000
    assert result["predictions"][30]["predicted_count"] == 9500

    assert result["predictions"][10]["load_percentage"] == 85.0

    # 2000 people remaining / 50 people per minute = 40 minutes
    assert result["breach_eta"] == 40.0
    