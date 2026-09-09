from app.services.risk_service import calculate_risk


def test_critical_risk():

    result = calculate_risk(
        crowd_pressure=0.95,
        growth_pressure=0.90,
        transport_pressure=0.90,
        weather_risk=0.85,
        nearby_zone_pressure=0.80,
        capacity_pressure=0.95,
    )

    assert result["risk_score"] == 90.25
    assert result["risk_level"] == "CRITICAL"

    assert "High crowd pressure" in result["reason_signals"]
    assert "Rapid crowd growth" in result["reason_signals"]
    assert "Transport pressure" in result["reason_signals"]
    assert "Severe weather conditions" in result["reason_signals"]


def test_safe_risk():

    result = calculate_risk(
        crowd_pressure=0.1,
        growth_pressure=0.1,
        transport_pressure=0.1,
        weather_risk=0.1,
        nearby_zone_pressure=0.1,
        capacity_pressure=0.1,
    )

    assert result["risk_score"] == 10.0
    assert result["risk_level"] == "SAFE"
    