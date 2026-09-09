from app.services.state_service import build_event_state
from app.services.simulation_service import simulate_crowd_change


def test_simulate_crowd_change():
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

    simulated = simulate_crowd_change(
        state=state,
        zone_id="ZONE_B",
        duration_minutes=10,
    )

    assert simulated["zones"]["ZONE_B"]["current_count"] == 8500
    assert simulated["zones"]["ZONE_B"]["load_percentage"] == 85.0

    # Original state must remain unchanged
    assert state["zones"]["ZONE_B"]["current_count"] == 8000