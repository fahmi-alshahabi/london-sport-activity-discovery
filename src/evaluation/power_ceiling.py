"""
Crossed-design power: variance, maximum attainable power, and the p x q surface.

Implements CA-01.A9. Basis: Westfall, Judd & Kenny (2014),
J. Exp. Psychol.: General 143(5), 2020-2045 - attested, source-reading matrix row 1.

Core result: when participants are crossed with tasks and both are sampled,
the stimulus-side variance term B/q does not vanish as participants increase.
Power therefore converges to a ceiling fixed by the task sample, not to 1.
A confirmatory target above that ceiling is unreachable at any participant count.

Notation:
    p = number of participants
    q = number of tasks (stimuli)
    A = participant-side variance component (participant x condition)
    B = stimulus-side variance component (stimulus x condition)
    C = participant x stimulus interaction + residual
    d = standardized effect size

Author: Fahmi Alshahabi (evaluation stream)
Status: v0.1 - variance components are inputs, not yet estimated for our design.
"""

import math
from statistics import NormalDist

_N = NormalDist()


# ---------------------------------------------------------------------
# Variance
# ---------------------------------------------------------------------

def se_squared(p, q, A, B, C):
    """
    Variance of the estimated effect for a crossed design.
    SE^2 = A/p + B/q + C/(p*q)
    """
    if p <= 0 or q <= 0:
        raise ValueError("p and q must be positive")
    return A / p + B / q + C / (p * q)


def se_squared_ceiling(q, B):
    """
    The variance floor as p -> infinity with q fixed.
    SE^2_floor = B/q
    """
    if q <= 0:
        raise ValueError("q must be positive")
    return B / q


def se(p, q, A, B, C):
    """Standard error."""
    return math.sqrt(se_squared(p, q, A, B, C))


def ceiling_se(q, B):
    """Smallest achievable standard error for a fixed q."""
    return math.sqrt(se_squared_ceiling(q, B))


# ---------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------

def _power_from_se(standard_error, d, alpha):
    """Two-sided power under a normal approximation."""
    if standard_error <= 0:
        return 1.0
    ncp = d / standard_error
    z = _N.inv_cdf(1 - alpha / 2)
    return _N.cdf(ncp - z) + _N.cdf(-ncp - z)


def power(p, q, A, B, C, d, alpha=0.05):
    """Achievable power for a crossed design at (p, q)."""
    return _power_from_se(se(p, q, A, B, C), d, alpha)


def max_attainable_power(q, B, d, alpha=0.05):
    """
    Ceiling: power as p -> infinity with q fixed. The CA-01.A9 quantity.
    Depends only on the task sample size and the stimulus-side variance.
    """
    return _power_from_se(ceiling_se(q, B), d, alpha)


# ---------------------------------------------------------------------
# Design surfaces and feasibility
# ---------------------------------------------------------------------

def power_surface(p_values, q_values, A, B, C, d, alpha=0.05):
    """
    Power over the participants x tasks grid.
    Returns {(p, q): power}. The A9 'participant x item power surface'.
    """
    return {
        (p, q): power(p, q, A, B, C, d, alpha)
        for p in p_values
        for q in q_values
    }


def min_tasks_for_target(target_power, B, d, alpha=0.05, q_max=10_000):
    """
    Smallest q whose CEILING reaches target_power.
    Below this q the target is unreachable at any participant count.
    Returns None if no q <= q_max suffices.
    """
    for q in range(1, q_max + 1):
        if max_attainable_power(q, B, d, alpha) >= target_power:
            return q
    return None


def min_participants_for_target(target_power, q, A, B, C, d,
                                alpha=0.05, p_max=100_000):
    """
    Smallest p reaching target_power at fixed q.
    Returns None when the ceiling at this q is below target - i.e. the
    design is infeasible regardless of recruitment.
    """
    if max_attainable_power(q, B, d, alpha) < target_power:
        return None
    for p in range(1, p_max + 1):
        if power(p, q, A, B, C, d, alpha) >= target_power:
            return p
    return None


def feasibility_report(target_power, p_budget, q_budget, A, B, C, d, alpha=0.05):
    """
    Design feasibility under budget caps. Supports the A9 rule that a
    confirmatory claim whose target exceeds the attainable ceiling is
    demoted to estimative BEFORE freeze.
    """
    ceiling = max_attainable_power(q_budget, B, d, alpha)
    achieved = power(p_budget, q_budget, A, B, C, d, alpha)
    q_needed = min_tasks_for_target(target_power, B, d, alpha)
    p_needed = min_participants_for_target(target_power, q_budget,
                                           A, B, C, d, alpha)
    return {
        "target_power": target_power,
        "p_budget": p_budget,
        "q_budget": q_budget,
        "ceiling_at_q_budget": ceiling,
        "achieved_at_budget": achieved,
        "target_reachable_at_q_budget": ceiling >= target_power,
        "min_tasks_for_target": q_needed,
        "min_participants_at_q_budget": p_needed,
        "verdict": (
            "FEASIBLE" if achieved >= target_power else
            "INFEASIBLE - ceiling below target; more TASKS required, "
            "recruitment cannot fix it" if ceiling < target_power else
            "REACHABLE - increase participants"
        ),
    }


# ---------------------------------------------------------------------
# Illustration (placeholder components - NOT our estimates)
# ---------------------------------------------------------------------

if __name__ == "__main__":
    A, B, C = 0.40, 0.25, 0.35
    d, alpha, target = 0.30, 0.05, 0.80

    print("Variance components (illustrative):", f"A={A} B={B} C={C}")
    print(f"Effect size d={d}, alpha={alpha}, target power={target}\n")

    print(f"{'p':>7} {'q':>5} {'SE':>9} {'power':>8} {'ceiling':>9}")
    for p in (50, 200, 1000, 100_000):
        for q in (10, 20, 50):
            print(f"{p:>7} {q:>5} {se(p,q,A,B,C):>9.4f} "
                  f"{power(p,q,A,B,C,d):>8.3f} "
                  f"{max_attainable_power(q,B,d):>9.3f}")

    print("\nThe ceiling depends only on q. Adding participants moves power")
    print("toward it and never past it.\n")

    print("Feasibility at a budget of 200 participants x 20 tasks:")
    for k, v in feasibility_report(target, 200, 20, A, B, C, d).items():
        print(f"  {k}: {v}")

    q_min = min_tasks_for_target(target, B, d)
    print(f"\nSmallest q whose ceiling reaches {target}: {q_min}")
