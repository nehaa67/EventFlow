from app.services.prediction_service import predict_crowd_growth
from app.services.risk_factor_service import calculate_risk_factors
from app.services.risk_service import calculate_risk


def analyze_zone(
    state: dict,
    zone_id: str,
):
    """
    Run the complete intelligence pipeline for one zone.

    Flow:
        State
        → Prediction
        → Risk Factors
        → Risk Score
    """

    # Step 1: Predict future crowd
    prediction = predict_crowd_growth(
        state=state,
        zone_id=zone_id,
    )

    # Step 2: Derive normalized risk factors
    factors = calculate_risk_factors(
        state=state,
        zone_id=zone_id,
        prediction=prediction,
    )

    # Step 3: Calculate final risk
    risk = calculate_risk(
        **factors
    )

    return {
        "zone_id": zone_id,
        "prediction": prediction,
        "risk": risk,
    }