def calculate_risk_factors(
    state: dict,
    zone_id: str,
    prediction: dict,
):
    """
    Derive normalized risk factors from the current event state
    and crowd prediction.

    This service does NOT calculate the final risk score.
    It prepares the six factors used by risk_service.py.
    """

    zone = state["zones"][zone_id]

    # ---------------------------------------------------------
    # 1. Crowd pressure
    # ---------------------------------------------------------
    capacity = zone.get("capacity", 0) or 0
    current_count = zone.get("current_count", 0) or 0

    if capacity > 0:
        crowd_pressure = current_count / capacity
    else:
        crowd_pressure = 0.0

    # ---------------------------------------------------------
    # 2. Growth pressure
    # ---------------------------------------------------------
    predictions = prediction.get("predictions", {})

    # Prediction API may return JSON keys as strings.
    predicted_30min = (
        predictions.get(30)
        or predictions.get("30")
    )

    if predicted_30min:
        predicted_load = (
            predicted_30min.get("load_percentage", 0) / 100
        )
        growth_pressure = predicted_load
    else:
        growth_pressure = 0.0

    # ---------------------------------------------------------
    # 3. Capacity pressure
    # ---------------------------------------------------------
    capacity_pressure = crowd_pressure

    # ---------------------------------------------------------
    # 4. Transport pressure
    # ---------------------------------------------------------
    transport_pressure = 0.0

    for transport in state.get("transport", {}).values():

        capacity = transport.get("capacity", 0) or 0
        current_load = transport.get("current_load", 0) or 0

        if capacity > 0:
            pressure = current_load / capacity

            transport_pressure = max(
                transport_pressure,
                pressure,
            )

    # ---------------------------------------------------------
    # 5. Weather risk
    # ---------------------------------------------------------
    weather_risk = 0.0

    conditions = state.get("conditions", {})

    weather_type = str(
        conditions.get("weather_type", "")
    ).upper()

    weather_scores = {
        "CLEAR": 0.0,
        "CLOUDY": 0.0,
        "LIGHT_RAIN": 0.3,
        "MODERATE_RAIN": 0.6,
        "HEAVY_RAIN": 1.0,
    }

    weather_risk = weather_scores.get(
        weather_type,
        0.0,
    )

    # ---------------------------------------------------------
    # 6. Nearby-zone pressure
    # ---------------------------------------------------------
    nearby_zone_pressure = 0.0

    for other_zone_id, other_zone in state["zones"].items():

        if str(other_zone_id) == str(zone_id):
            continue

        other_capacity = other_zone.get("capacity", 0) or 0
        other_count = other_zone.get("current_count", 0) or 0

        if other_capacity > 0:
            pressure = other_count / other_capacity

            nearby_zone_pressure = max(
                nearby_zone_pressure,
                pressure,
            )

    # ---------------------------------------------------------
    # Normalize all factors to 0–1
    # ---------------------------------------------------------
    factors = {
        "crowd_pressure": crowd_pressure,
        "growth_pressure": growth_pressure,
        "transport_pressure": transport_pressure,
        "weather_risk": weather_risk,
        "nearby_zone_pressure": nearby_zone_pressure,
        "capacity_pressure": capacity_pressure,
    }

    factors = {
        name: max(0.0, min(1.0, float(value)))
        for name, value in factors.items()
    }

    return factors