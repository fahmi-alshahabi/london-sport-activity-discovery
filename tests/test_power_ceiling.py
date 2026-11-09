"""
Tests for src/evaluation/power_ceiling.py (CA-01.A9).

Scope: these tests encode the properties the module's own docstrings assert.
They check internal consistency and the qualitative behaviour of the crossed-design
variance decomposition. They do NOT validate that the decomposition is the right
model for our design — that is the recovery test at the bottom, which is owed.

Run:  python -m pytest test_power_ceiling.py -q
"""

import math
import pytest

import power_ceiling as pc


A, B, C = 0.40, 0.25, 0.35
D, ALPHA = 0.30, 0.05


# ---------------------------------------------------------------------
# 1. Variance formula
# ---------------------------------------------------------------------

def test_se_squared_matches_formula():
    p, q = 37, 13
    assert pc.se_squared(p, q, A, B, C) == pytest.approx(A / p + B / q + C / (p * q))


def test_se_is_sqrt_of_se_squared():
    assert pc.se(50, 20, A, B, C) == pytest.approx(math.sqrt(pc.se_squared(50, 20, A, B, C)))


@pytest.mark.parametrize("p,q", [(0, 10), (10, 0), (-1, 10), (10, -1)])
def test_nonpositive_design_sizes_raise(p, q):
    with pytest.raises(ValueError):
        pc.se_squared(p, q, A, B, C)


def test_ceiling_requires_positive_q():
    with pytest.raises(ValueError):
        pc.se_squared_ceiling(0, B)


# ---------------------------------------------------------------------
# 2. Monotonicity
# ---------------------------------------------------------------------

def test_se_squared_strictly_decreasing_in_participants():
    vals = [pc.se_squared(p, 20, A, B, C) for p in (10, 50, 200, 1000)]
    assert all(x > y for x, y in zip(vals, vals[1:]))


def test_se_squared_strictly_decreasing_in_tasks():
    vals = [pc.se_squared(200, q, A, B, C) for q in (5, 10, 40, 200)]
    assert all(x > y for x, y in zip(vals, vals[1:]))


def test_power_increasing_in_participants():
    vals = [pc.power(p, 20, A, B, C, D) for p in (10, 50, 200, 1000)]
    assert all(x < y for x, y in zip(vals, vals[1:]))


# ---------------------------------------------------------------------
# 3. The ceiling — the CA-01.A9 result
# ---------------------------------------------------------------------

def test_variance_never_reaches_the_floor_at_finite_p():
    """B/q does not vanish; A/p + C/(pq) is strictly positive for finite p."""
    for p in (1, 10, 10_000, 10_000_000):
        assert pc.se_squared(p, 20, A, B, C) > pc.se_squared_ceiling(20, B)


def test_variance_converges_to_the_floor():
    floor = pc.se_squared_ceiling(20, B)
    assert pc.se_squared(10**9, 20, A, B, C) == pytest.approx(floor, rel=1e-6)


def test_power_bounded_by_ceiling_at_every_p():
    ceiling = pc.max_attainable_power(20, B, D)
    for p in (1, 10, 100, 10_000, 10_000_000):
        assert pc.power(p, 20, A, B, C, D) <= ceiling


def test_ceiling_does_not_depend_on_participant_or_residual_variance():
    """The ceiling is fixed by the task sample. A and C cannot move it."""
    base = pc.max_attainable_power(20, B, D)
    for A_alt, C_alt in [(0.01, 0.01), (5.0, 5.0), (0.4, 9.9)]:
        assert pc.max_attainable_power(20, B, D) == base
        # and the achievable power stays under it whatever A and C are
        assert pc.power(10**7, 20, A_alt, B, C_alt, D) <= base + 1e-12


def test_ceiling_rises_with_more_tasks():
    vals = [pc.max_attainable_power(q, B, D) for q in (5, 10, 40, 200)]
    assert all(x < y for x, y in zip(vals, vals[1:]))


# ---------------------------------------------------------------------
# 4. Design solvers
# ---------------------------------------------------------------------

def test_min_tasks_is_the_smallest_q_whose_ceiling_reaches_target():
    target = 0.80
    q = pc.min_tasks_for_target(target, B, D)
    assert q is not None
    assert pc.max_attainable_power(q, B, D) >= target
    assert pc.max_attainable_power(q - 1, B, D) < target


def test_min_participants_returns_none_exactly_when_infeasible():
    """None must mean 'unreachable at any p', never 'search gave up'."""
    target = 0.80
    infeasible_q = pc.min_tasks_for_target(target, B, D) - 1
    assert pc.max_attainable_power(infeasible_q, B, D) < target
    assert pc.min_participants_for_target(target, infeasible_q, A, B, C, D) is None

    feasible_q = pc.min_tasks_for_target(target, B, D) + 10
    p = pc.min_participants_for_target(target, feasible_q, A, B, C, D)
    assert p is not None
    assert pc.power(p, feasible_q, A, B, C, D) >= target
    assert pc.power(p - 1, feasible_q, A, B, C, D) < target


# ---------------------------------------------------------------------
# 5. Feasibility report — the artefact that gates a confirmatory claim
# ---------------------------------------------------------------------

def test_report_flags_task_starved_design_as_infeasible():
    """More participants must not be offered as a fix when q is the binding constraint."""
    target = 0.95
    r = pc.feasibility_report(target, p_budget=100_000, q_budget=5, A=A, B=B, C=C, d=D)
    assert r["target_reachable_at_q_budget"] is False
    assert r["min_participants_at_q_budget"] is None
    assert "INFEASIBLE" in r["verdict"]
    assert "TASKS" in r["verdict"]


def test_report_internally_consistent():
    for target, p_b, q_b in [(0.80, 200, 20), (0.95, 50, 5), (0.50, 1000, 100)]:
        r = pc.feasibility_report(target, p_b, q_b, A, B, C, D)
        assert r["achieved_at_budget"] <= r["ceiling_at_q_budget"]
        assert r["target_reachable_at_q_budget"] == (r["ceiling_at_q_budget"] >= target)
        if r["verdict"] == "FEASIBLE":
            assert r["achieved_at_budget"] >= target
        if r["verdict"].startswith("INFEASIBLE"):
            assert r["ceiling_at_q_budget"] < target


# ---------------------------------------------------------------------
# 6. Recovery test — OWED (Fahmi)
# ---------------------------------------------------------------------

@pytest.mark.skip(reason="OWED: data-generating model must be authored by Fahmi")
def test_simulation_recovers_the_analytic_standard_error():
    """
    Simulate a crossed participant x task design with KNOWN variance components,
    estimate the effect many times, and check the empirical SD of the estimates
    matches pc.se(p, q, A, B, C).

    This is the test that actually validates the decomposition against our design
    rather than against its own algebra. It requires deciding what the data-generating
    model is — which is a modelling judgment, not a coding one:

      - are participant effects and task effects both random and crossed?
      - is the condition effect within-participant and within-task?
      - do origins and publishers add a further nesting level that breaks the
        two-component structure? (see F-04 grouping keys)

    Until the DGP is written, the module's algebra is verified but its applicability
    to our design is not.
    """
