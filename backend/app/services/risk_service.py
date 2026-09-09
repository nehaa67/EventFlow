def calculate_risk(
    crowd_pressure: float,
    growth_pressure: float,
    transport_pressure: float,
    weather_risk: float,
    nearby_zone_pressure: float,
    capacity_pressure: float,
):
    """
    Calculate a deterministic 0–100 event risk score.

    All input factors should be normalized between 0 and 1.
    """

    weights = {
        "crowd_pressure": 0.30,
        "growth_pressure": 0.20,
        "transport_pressure": 0.15,
        "weather_risk": 0.15,
        "nearby_zone_pressure": 0.10,
        "capacity_pressure": 0.10,
    }

    factors = {
        "crowd_pressure": crowd_pressure,
        "growth_pressure": growth_pressure,
        "transport_pressure": transport_pressure,
        "weather_risk": weather_risk,
        "nearby_zone_pressure": nearby_zone_pressure,
        "capacity_pressure": capacity_pressure,
    }

    # Keep every factor within 0–1
    factors = {
        name: max(0.0, min(1.0, value))
        for name, value in factors.items()
    }

    weighted_score = sum(
        factors[name] * weights[name]
        for name in weights
    )

    risk_score = round(weighted_score * 100, 2)

    if risk_score <= 30:
        risk_level = "SAFE"
    elif risk_score <= 60:
        risk_level = "WARNING"
    elif risk_score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    reasons = []

    if crowd_pressure >= 0.7:
        reasons.append("High crowd pressure")

    if growth_pressure >= 0.7:
        reasons.append("Rapid crowd growth")

    if transport_pressure >= 0.7:
        reasons.append("Transport pressure")

    if weather_risk >= 0.7:
        reasons.append("Severe weather conditions")

    if nearby_zone_pressure >= 0.7:
        reasons.append("Pressure from nearby zones")

    if capacity_pressure >= 0.7:
        reasons.append("High capacity utilization")

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason_signals": reasons,
        "factors": factors,
    }