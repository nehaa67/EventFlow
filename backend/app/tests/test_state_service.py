from app.services.state_service import build_event_state


def test_build_event_state():

    state = build_event_state(
        event_id="EV001",

        zones={
            "ZONE_B": {
                "capacity": 10000,
                "current_count": 8200,
                "arrival_rate": 850,
                "departure_rate": 400,
            }
        },

        transport={
            "METRO_B": {
                "capacity": 10000,
                "load": 9100,
                "status": "DELAYED",
            }
        },

        conditions={
            "rain": "HEAVY"
        },

        incidents=[]
    )

    assert state["event_id"] == "EV001"
    assert state["zones"]["ZONE_B"]["current_count"] == 8200
    assert state["transport"]["METRO_B"]["status"] == "DELAYED"