from copy import deepcopy


# =========================================================
# INTERVENTION EFFECTS
# =========================================================
# MVP simulation assumptions.
#
# These values are NOT real-world measurements.
# They represent the estimated effect of each intervention
# inside the EventFlow what-if simulation.
#
# 1 -> Open Alternate Exit
# 2 -> Increase Shuttle Service
# 3 -> Crowd Diversion
# =========================================================

INTERVENTION_EFFECTS = {
    1: {
        "extra_outflow": 25.0,
        "extra_inflow": 0.0,
        "description": (
            "Increases crowd outflow through an alternate exit."
        ),
    },
    2: {
        "extra_outflow": 15.0,
        "extra_inflow": -10.0,
        "description": (
            "Reduces crowd pressure through additional "
            "transport capacity."
        ),
    },
    3: {
        "extra_outflow": 20.0,
        "extra_inflow": -15.0,
        "description": (
            "Redirects part of the crowd toward "
            "less congested areas."
        ),
    },
}


# =========================================================
# BASIC CROWD SIMULATION
# =========================================================

def simulate_crowd_change(
    state: dict,
    zone_id: str,
    duration_minutes: int,
    extra_inflow: float = 0,
    extra_outflow: float = 0,
):
    """
    Simulate how crowd conditions change in a zone.

    The original event state is never modified.
    """

    simulated_state = deepcopy(state)

    # -----------------------------------------------------
    # Validate zone
    # -----------------------------------------------------

    if zone_id not in simulated_state.get("zones", {}):
        raise ValueError(
            f"Zone {zone_id} not found in event state."
        )

    zone = simulated_state["zones"][zone_id]

    # -----------------------------------------------------
    # Read current values
    # -----------------------------------------------------

    current_count = float(
        zone.get("current_count") or 0
    )

    arrival_rate = float(
        zone.get("arrival_rate") or 0
    )

    departure_rate = float(
        zone.get("departure_rate") or 0
    )

    capacity = float(
        zone.get("capacity") or 0
    )

    # -----------------------------------------------------
    # Validate capacity
    # -----------------------------------------------------

    if capacity <= 0:
        raise ValueError(
            f"Zone {zone_id} has no valid capacity."
        )

    # -----------------------------------------------------
    # Calculate net crowd movement
    # -----------------------------------------------------

    net_rate = (
        arrival_rate
        + extra_inflow
        - departure_rate
        - extra_outflow
    )

    # -----------------------------------------------------
    # Calculate future crowd
    # -----------------------------------------------------

    future_count = (
        current_count
        + net_rate * duration_minutes
    )

    # Crowd cannot be negative.
    future_count = max(
        0,
        future_count,
    )

    # -----------------------------------------------------
    # Calculate future load
    # -----------------------------------------------------

    load_percentage = (
        future_count / capacity
    ) * 100

    # -----------------------------------------------------
    # Update simulated state only
    # -----------------------------------------------------

    zone["current_count"] = round(
        future_count,
        2,
    )

    zone["load_percentage"] = round(
        load_percentage,
        2,
    )

    return simulated_state


# =========================================================
# WHAT-IF INTERVENTION SIMULATION
# =========================================================

def simulate_intervention(
    state: dict,
    zone_id: str,
    intervention_id: int,
    duration_minutes: int = 30,
):
    """
    Run a what-if simulation for a database-defined
    intervention.

    The simulation compares:

        1. BASELINE
           What happens without intervention.

        2. INTERVENTION
           What happens when the selected intervention
           is applied.

    The original event state is never modified.

    All intervention effects are explicit MVP
    simulation assumptions.
    """

    # -----------------------------------------------------
    # Validate intervention
    # -----------------------------------------------------

    if intervention_id not in INTERVENTION_EFFECTS:
        raise ValueError(
            f"Unsupported intervention_id: "
            f"{intervention_id}"
        )

    # -----------------------------------------------------
    # Validate duration
    # -----------------------------------------------------

    if duration_minutes <= 0:
        raise ValueError(
            "duration_minutes must be greater than zero."
        )

    # -----------------------------------------------------
    # Validate zone
    # -----------------------------------------------------

    if zone_id not in state.get("zones", {}):
        raise ValueError(
            f"Zone {zone_id} not found in event state."
        )

    zone = state["zones"][zone_id]

    # -----------------------------------------------------
    # Read current zone values
    # -----------------------------------------------------

    current_count = float(
        zone.get("current_count") or 0
    )

    capacity = float(
        zone.get("capacity") or 0
    )

    arrival_rate = float(
        zone.get("arrival_rate") or 0
    )

    departure_rate = float(
        zone.get("departure_rate") or 0
    )

    # -----------------------------------------------------
    # Validate capacity
    # -----------------------------------------------------

    if capacity <= 0:
        raise ValueError(
            f"Zone {zone_id} has no valid capacity."
        )

    # =====================================================
    # 1. BASELINE
    # =====================================================
    # No intervention is applied.
    # =====================================================

    baseline_net_rate = (
        arrival_rate
        - departure_rate
    )

    baseline_count = (
        current_count
        + baseline_net_rate
        * duration_minutes
    )

    baseline_count = max(
        0,
        baseline_count,
    )

    baseline_load = (
        baseline_count / capacity
    ) * 100

    # =====================================================
    # 2. INTERVENTION SCENARIO
    # =====================================================

    effect = INTERVENTION_EFFECTS[
        intervention_id
    ]

    simulated_state = simulate_crowd_change(
        state=state,
        zone_id=zone_id,
        duration_minutes=duration_minutes,
        extra_inflow=effect["extra_inflow"],
        extra_outflow=effect["extra_outflow"],
    )

    simulated_zone = (
        simulated_state["zones"][zone_id]
    )

    intervention_count = float(
        simulated_zone["current_count"]
    )

    intervention_load = float(
        simulated_zone["load_percentage"]
    )

    # =====================================================
    # 3. MEASURE INTERVENTION IMPACT
    # =====================================================

    # Positive value means the intervention reduced
    # the projected crowd.
    crowd_reduction = (
        baseline_count
        - intervention_count
    )

    # Positive value means the intervention reduced
    # capacity utilization.
    load_reduction = (
        baseline_load
        - intervention_load
    )

    # Percentage improvement relative to baseline.
    if baseline_count > 0:
        improvement_percentage = (
            crowd_reduction
            / baseline_count
        ) * 100
    else:
        improvement_percentage = 0.0

    # =====================================================
    # 4. CAPACITY STATUS
    # =====================================================

    baseline_over_capacity = (
        baseline_count > capacity
    )

    intervention_over_capacity = (
        intervention_count > capacity
    )

    # =====================================================
    # 5. RETURN RESULT
    # =====================================================

    return {
        "intervention_id": intervention_id,
        "zone_id": zone_id,
        "duration_minutes": duration_minutes,
        "simulation_status": "SIMULATED",

        # -------------------------------------------------
        # BASELINE
        # -------------------------------------------------

        "baseline": {
            "current_count": round(
                current_count,
                2,
            ),
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

        # -------------------------------------------------
        # INTERVENTION
        # -------------------------------------------------

        "intervention": {
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

        # -------------------------------------------------
        # IMPACT
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ASSUMPTIONS
        # -------------------------------------------------

        "assumptions": {
            "extra_inflow": effect[
                "extra_inflow"
            ],
            "extra_outflow": effect[
                "extra_outflow"
            ],
            "description": effect[
                "description"
            ],
        },

        # -------------------------------------------------
        # FULL SIMULATED STATE
        # -------------------------------------------------

        "simulated_state": simulated_state,
    }

