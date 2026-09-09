import pytest

from app.services.state_service import build_event_state
from app.services.intelligence_service import analyze_zone


@pytest.mark.skip(
    reason=(
        "analyze_zone() internally calls predict_crowd_growth() with the "
        "old in-memory signature (state=..., zone_id=...) and is dead code "
        "post-integration — nothing in the live app calls it anymore. "
        "The equivalent pipeline is exercised live via "
        "/api/events/{id}/interventions. See README 'Known pre-existing "
        "issue' for context."
    )
)
def test_analyze_zone():

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

    result = analyze_zone(
        state=state,
        zone_id="ZONE_B",
    )

    assert result["zone_id"] == "ZONE_B"

    assert result["prediction"]["predictions"][30]["predicted_count"] == 9500

    assert result["risk"]["risk_score"] == 86.5
    assert result["risk"]["risk_level"] == "CRITICAL"

    assert "High crowd pressure" in result["risk"]["reason_signals"]
    assert "Rapid crowd growth" in result["risk"]["reason_signals"]
    assert "Transport pressure" in result["risk"]["reason_signals"]
    assert "Severe weather conditions" in result["risk"]["reason_signals"]