from sqlalchemy.orm import Session

from app.models import Intervention
from app.services.simulation_service import simulate_intervention


def rank_interventions(
    db: Session,
    event_id: int,
    risk_result: dict,
    root_causes: dict,
    state: dict,
    zone_id: str,
    duration_minutes: int = 30,
):
    interventions = (
        db.query(Intervention)
        .filter(Intervention.event_id == event_id)
        .order_by(Intervention.intervention_id)
        .all()
    )

    if not interventions:
        return {
            "event_id": event_id,
            "recommended_intervention": None,
            "interventions": [],
        }

    risk_score = float(risk_result.get("risk_score", 0.0))
    risk_level = risk_result.get("risk_level", "UNKNOWN")

    causes = root_causes.get("root_causes", [])

    cause_factors = {
        cause.get("factor")
        for cause in causes
        if cause.get("factor")
    }

    results = []

    for intervention in interventions:
        intervention_id = intervention.intervention_id

        try:
            simulation = simulate_intervention(
                state=state,
                zone_id=str(zone_id),
                intervention_id=intervention_id,
                duration_minutes=duration_minutes,
            )

        except ValueError as exc:
            results.append({
                "intervention_id": intervention_id,
                "intervention_name": intervention.intervention_name,
                "intervention_type": intervention.intervention_type,
                "description": intervention.description,
                "target_area": intervention.target_area,
                "priority": intervention.priority,
                "status": intervention.status,
                "simulation_status": "FAILED",
                "effectiveness_score": 0.0,
                "estimated_risk_reduction": 0.0,
                "estimated_post_risk": risk_score,
                "simulation_outcome": "Simulation unavailable",
                "reason": f"Simulation unavailable: {exc}",
            })
            continue

        baseline = simulation.get("baseline", {})
        intervention_result = simulation.get("intervention", {})
        impact = simulation.get("impact", {})

        baseline_count = float(
            baseline.get("projected_count", 0.0)
        )

        intervention_count = float(
            intervention_result.get("projected_count", 0.0)
        )

        baseline_load = float(
            baseline.get("projected_load_percentage", 0.0)
        )

        intervention_load = float(
            intervention_result.get(
                "projected_load_percentage",
                0.0,
            )
        )

        crowd_reduction = float(
            impact.get("crowd_reduction", 0.0)
        )

        load_reduction = float(
            impact.get(
                "load_reduction_percentage_points",
                0.0,
            )
        )

        improvement_percentage = float(
            impact.get("improvement_percentage", 0.0)
        )

        baseline_over_capacity = bool(
            baseline.get("over_capacity", False)
        )

        intervention_over_capacity = bool(
            intervention_result.get(
                "over_capacity",
                False,
            )
        )

        capacity_resolved = (
            baseline_over_capacity
            and not intervention_over_capacity
        )

        crowd_improvement = 0.0

        if baseline_count > 0:
            crowd_improvement = (
                crowd_reduction / baseline_count
            )

        load_improvement = 0.0

        if baseline_load > 0:
            load_improvement = (
                load_reduction / baseline_load
            )

        crowd_improvement = max(
            0.0,
            min(1.0, crowd_improvement),
        )

        load_improvement = max(
            0.0,
            min(1.0, load_improvement),
        )

        effectiveness_score = (
            0.60 * crowd_improvement
            + 0.40 * load_improvement
        )

        if capacity_resolved:
            effectiveness_score += 0.15

        effectiveness_score = max(
            0.0,
            min(1.0, effectiveness_score),
        )

        estimated_risk_reduction = round(
            risk_score * effectiveness_score,
            2,
        )

        estimated_post_risk = round(
            max(
                0.0,
                risk_score - estimated_risk_reduction,
            ),
            2,
        )

        reasons = []

        intervention_name = (
            intervention.intervention_name or ""
        ).lower()

        intervention_type = (
            intervention.intervention_type or ""
        ).lower()

        if "crowd_pressure" in cause_factors:
            if (
                "gate" in intervention_name
                or "crowd" in intervention_type
                or "diversion" in intervention_name
            ):
                reasons.append(
                    "Addresses high crowd pressure"
                )

        if "growth_pressure" in cause_factors:
            if (
                "gate" in intervention_name
                or "crowd" in intervention_type
                or "diversion" in intervention_name
            ):
                reasons.append(
                    "Addresses projected crowd growth"
                )

        if "transport_pressure" in cause_factors:
            if (
                "transport" in intervention_type
                or "shuttle" in intervention_name
            ):
                reasons.append(
                    "Addresses transport pressure"
                )

        if "weather_risk" in cause_factors:
            if (
                "transport" in intervention_type
                or "shuttle" in intervention_name
            ):
                reasons.append(
                    "Supports movement during severe weather"
                )

        if "nearby_zone_pressure" in cause_factors:
            if (
                "diversion" in intervention_name
                or "crowd" in intervention_type
                or "gate" in intervention_name
            ):
                reasons.append(
                    "Can redistribute crowd pressure"
                )

        if "capacity_pressure" in cause_factors:
            if (
                "gate" in intervention_name
                or "diversion" in intervention_name
                or "crowd" in intervention_type
            ):
                reasons.append(
                    "Addresses capacity pressure"
                )

        if crowd_reduction > 0:
            reasons.append(
                f"Simulation reduces projected crowd by "
                f"{round(crowd_reduction, 2)} people"
            )

        if load_reduction > 0:
            reasons.append(
                f"Simulation reduces projected load by "
                f"{round(load_reduction, 2)} percentage points"
            )

        if capacity_resolved:
            reasons.append(
                "Simulation returns the zone below capacity"
            )

        if not reasons:
            reasons.append(
                "Limited measurable improvement in the current simulation"
            )

        if capacity_resolved:
            simulation_outcome = (
                "Returns zone below capacity"
            )

        elif (
            baseline_over_capacity
            and intervention_over_capacity
        ):
            simulation_outcome = (
                "Reduces overload but zone remains over capacity"
            )

        elif (
            not baseline_over_capacity
            and not intervention_over_capacity
        ):
            if load_reduction > 0:
                simulation_outcome = (
                    "Improves projected crowd conditions"
                )
            else:
                simulation_outcome = (
                    "No meaningful simulated improvement"
                )

        else:
            simulation_outcome = (
                "Requires further evaluation"
            )

        results.append({
            "intervention_id": intervention_id,
            "intervention_name": intervention.intervention_name,
            "intervention_type": intervention.intervention_type,
            "description": intervention.description,
            "target_area": intervention.target_area,
            "priority": intervention.priority,
            "status": intervention.status,
            "simulation_status": simulation.get(
                "simulation_status",
                "SIMULATED",
            ),
            "effectiveness_score": round(
                effectiveness_score,
                4,
            ),
            "estimated_risk_reduction": (
                estimated_risk_reduction
            ),
            "estimated_post_risk": (
                estimated_post_risk
            ),
            "simulation_outcome": (
                simulation_outcome
            ),
            "baseline": {
                "projected_count": round(
                    baseline_count,
                    2,
                ),
                "projected_load_percentage": round(
                    baseline_load,
                    2,
                ),
                "over_capacity": (
                    baseline_over_capacity
                ),
            },
            "intervention_result": {
                "projected_count": round(
                    intervention_count,
                    2,
                ),
                "projected_load_percentage": round(
                    intervention_load,
                    2,
                ),
                "over_capacity": (
                    intervention_over_capacity
                ),
            },
            "impact": {
                "crowd_reduction": round(
                    crowd_reduction,
                    2,
                ),
                "load_reduction_percentage_points": round(
                    load_reduction,
                    2,
                ),
                "improvement_percentage": round(
                    improvement_percentage,
                    2,
                ),
            },
            "reason": "; ".join(reasons),
        })

    results.sort(
        key=lambda item: (
            item["effectiveness_score"],
            (
                1
                if item.get(
                    "intervention_result",
                    {},
                ).get(
                    "over_capacity",
                    True,
                ) is False
                else 0
            ),
            item.get(
                "impact",
                {},
            ).get(
                "load_reduction_percentage_points",
                0.0,
            ),
            item.get(
                "impact",
                {},
            ).get(
                "crowd_reduction",
                0.0,
            ),
        ),
        reverse=True,
    )

    for index, intervention in enumerate(
        results,
        start=1,
    ):
        intervention["rank"] = index

    recommended = results[0] if results else None

    return {
        "event_id": event_id,
        "affected_zone_id": str(zone_id),
        "duration_minutes": duration_minutes,
        "current_risk_score": risk_score,
        "current_risk_level": risk_level,
        "recommended_intervention": recommended,
        "interventions": results,
    }