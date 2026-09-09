def identify_root_causes(
    risk_result: dict,
    state: dict,
    zone_id: str,
):
    """
    Identify the main causes contributing to a zone's risk.

    This service explains the risk result.
    It does not calculate or modify the risk score.
    """

    factors = risk_result["factors"]
    causes = []

    # Crowd-related cause
    if factors["crowd_pressure"] >= 0.7:
        causes.append({
            "cause": "High crowd occupancy",
            "factor": "crowd_pressure",
            "severity": factors["crowd_pressure"],
        })

    # Growth-related cause
    if factors["growth_pressure"] >= 0.7:
        causes.append({
            "cause": "Rapid crowd growth",
            "factor": "growth_pressure",
            "severity": factors["growth_pressure"],
        })

    # Transport-related cause
    if factors["transport_pressure"] >= 0.7:
        causes.append({
            "cause": "Transport pressure",
            "factor": "transport_pressure",
            "severity": factors["transport_pressure"],
        })

    # Weather-related cause
    if factors["weather_risk"] >= 0.7:
        causes.append({
            "cause": "Severe weather conditions",
            "factor": "weather_risk",
            "severity": factors["weather_risk"],
        })

    # Nearby-zone cause
    if factors["nearby_zone_pressure"] >= 0.7:
        causes.append({
            "cause": "Pressure from nearby zones",
            "factor": "nearby_zone_pressure",
            "severity": factors["nearby_zone_pressure"],
        })

    # Capacity cause
    if factors["capacity_pressure"] >= 0.7:
        causes.append({
            "cause": "High capacity utilization",
            "factor": "capacity_pressure",
            "severity": factors["capacity_pressure"],
        })

    # Sort strongest causes first
    causes.sort(
        key=lambda item: item["severity"],
        reverse=True,
    )

    return {
        "zone_id": zone_id,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "root_causes": causes,
    }