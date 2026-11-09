"""
F-06 — sizing harness (SCAFFOLD).

Purpose: for each confirmatory claim, report the minimum task count whose attainable
power ceiling reaches the target, the participant count needed at a given task budget,
and whether the claim survives a declared origin-variance sensitivity range.

Design decision (F-06/CA-01.A9, 18 Aug 2026): route (c) — size on the two-component
crossed model in power_ceiling.py, and report a declared sensitivity analysis for
origin/publisher variance rather than adding a third level that cannot currently be
estimated. Origins are not recorded in condition-manifest.json (F-12 M-4), so a third
component would be sized against invented numbers.

Primary design variable is TASK COUNT, not participant count. This is the CA-01.A9
result and it is why the report leads with min-q.

Status: SCAFFOLD. Orchestration and reporting are implemented. Every number that
enters a decision is either a RATIFY placeholder or an AUTHOR-FAHMI field.

Author: Fahmi Alshahabi (evaluation stream)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json

import power_ceiling as pc


# ---------------------------------------------------------------------
# 1. Inputs
# ---------------------------------------------------------------------

@dataclass
class VarianceComponents:
    """
    Crossed-design variance components for one claim.

    AUTHOR-FAHMI: these are the load-bearing inputs. They must come from one of:
      - a pilot with enough tasks AND enough origins to separate the components,
      - a published estimate you have attested, or
      - a declared plausible range treated as a sensitivity, not a point estimate.

    Do not carry the illustrative values from power_ceiling.py's __main__ block into
    a decision. They are placeholders.
    """
    A: float          # participant-side (participant x condition)
    B: float          # stimulus-side (task x condition) — sets the ceiling
    C: float          # participant x task interaction + residual
    source: str = "RATIFY"     # provenance of these numbers
    is_placeholder: bool = True


@dataclass
class Claim:
    """One confirmatory claim to be sized."""
    claim_id: str
    description: str
    d: float                          # effect size / margin — RATIFY in F-02
    target_power: float               # RATIFY
    alpha: float                      # RATIFY
    components: VarianceComponents
    q_budget: Optional[int] = None    # tasks available
    p_budget: Optional[int] = None    # participants available
    margin_source: str = "RATIFY"


# ---------------------------------------------------------------------
# 2. Origin-variance sensitivity (route c)
# ---------------------------------------------------------------------

def inflate_B(B: float, rho: float) -> float:
    """
    Represent absorbed origin/publisher variance by inflating the stimulus-side
    component: B_effective = B * (1 + rho).

    AUTHOR-FAHMI: this is ONE candidate parameterisation, not the only one, and you
    are signing it. Accept it, or replace it with a model you can defend. Questions
    it begs, which you should answer in F-06's write-up:
      - is origin variance additive to B, or does it also inflate C?
      - is rho bounded above by anything principled, or is the range a judgment?
      - if tasks are sampled within a small number of origins, does q even index the
        right thing, or is the effective item sample closer to the origin count?

    That last question is the sharp one: if origin effects dominate, the effective
    ceiling may be set by the number of ORIGINS, not the number of tasks, and route
    (c) would be understating the problem rather than bounding it.
    """
    if rho < 0:
        raise ValueError("rho must be non-negative")
    return B * (1.0 + rho)


# AUTHOR-FAHMI: declare the sensitivity range BEFORE running, not after seeing results.
RHO_RANGE: tuple[float, ...] = (0.00, 0.25, 0.50, 1.00)   # AUTHOR-FAHMI: declared before running


# ---------------------------------------------------------------------
# 3. Sizing
# ---------------------------------------------------------------------

def size_claim(claim: Claim, rho: float = 0.0) -> dict:
    """Size one claim at one origin-variance assumption."""
    if claim.d == 0.0:
        raise ValueError(
            f"{claim.claim_id}: effect size / margin d is 0.0. A zero effect is "
            "undetectable at any task or participant count, so this is always an "
            "unset RATIFY placeholder rather than a design finding. Set d from F-02 "
            "before sizing."
        )
    v = claim.components
    B_eff = inflate_B(v.B, rho)

    min_q = pc.min_tasks_for_target(claim.target_power, B_eff, claim.d, claim.alpha)
    ceiling_at_budget = (
        pc.max_attainable_power(claim.q_budget, B_eff, claim.d, claim.alpha)
        if claim.q_budget else None
    )
    min_p = (
        pc.min_participants_for_target(
            claim.target_power, claim.q_budget, v.A, B_eff, v.C, claim.d, claim.alpha
        ) if claim.q_budget else None
    )

    return {
        "claim_id": claim.claim_id,
        "rho": rho,
        "B_effective": B_eff,
        "min_tasks_for_target": min_q,
        "ceiling_at_q_budget": ceiling_at_budget,
        "min_participants_at_q_budget": min_p,
        "reachable_at_budget": (
            ceiling_at_budget >= claim.target_power
            if ceiling_at_budget is not None else None
        ),
    }


def sensitivity_surface(claim: Claim, rho_range=None) -> list[dict]:
    """Size one claim across the declared origin-variance range."""
    rhos = rho_range if rho_range is not None else RHO_RANGE
    if not rhos:
        raise ValueError(
            "RHO_RANGE is empty. Declare the sensitivity range before running — "
            "choosing it after seeing results is outcome-dependent."
        )
    return [size_claim(claim, rho) for rho in rhos]


# ---------------------------------------------------------------------
# 4. Demotion rule
# ---------------------------------------------------------------------

def demotion_verdict(rows: list[dict], claim: Claim) -> str:
    """
    Pre-declared governance rule (AUTHOR-FAHMI, 18 Aug 2026).

    STRICT READING, chosen deliberately: a claim remains confirmatory only if its
    target is reachable at EVERY rho in the declared sensitivity range, including
    the upper bound. A claim that is comfortably powered under zero origin variance
    but fails at rho_max is demoted.

    The rationale is that the sensitivity range is a statement about what we do not
    know. Retaining a confirmatory claim that survives only under the most
    favourable assumption in that range would be asserting the assumption rather
    than testing under it. The cost is accepted: the rule is conservative and will
    demote some claims that a less cautious range would have kept.

    Verdicts:
      NOT_SIZEABLE       — inputs are unset RATIFY placeholders; nothing was sized.
      INSUFFICIENT_BUDGET — sized, but no task budget was supplied to judge against.
      CONFIRMATORY       — target reachable across the whole declared rho range.
      ESTIMATIVE         — reachable at some rho but not all; demoted before freeze.
    """
    if claim.margin_source.upper().startswith("RATIFY") or claim.components.is_placeholder:
        return "NOT_SIZEABLE — margins/components are unratified placeholders"
    reachable = [r["reachable_at_budget"] for r in rows if r["reachable_at_budget"] is not None]
    if not reachable:
        return "INSUFFICIENT_BUDGET — no task budget supplied"
    if all(reachable):
        return "CONFIRMATORY"
    return "ESTIMATIVE"


# ---------------------------------------------------------------------
# 5. Reporting
# ---------------------------------------------------------------------

def format_report(claim: Claim, rows: list[dict]) -> str:
    """Human-readable sizing report for one claim."""
    v = claim.components
    out = [
        f"CLAIM {claim.claim_id} — {claim.description}",
        f"  target power {claim.target_power}  alpha {claim.alpha}  d {claim.d}"
        f"   [margin source: {claim.margin_source}]",
        f"  components A={v.A} B={v.B} C={v.C}   [source: {v.source}]",
    ]
    if v.is_placeholder:
        out.append("  *** PLACEHOLDER COMPONENTS — not a sizing decision ***")
    out.append(f"  budgets: q={claim.q_budget}  p={claim.p_budget}")
    out.append("")
    out.append(f"  {'rho':>6} {'B_eff':>8} {'min_q':>7} {'ceiling@q':>10} {'min_p@q':>9}")
    for r in rows:
        ceil = f"{r['ceiling_at_q_budget']:.3f}" if r["ceiling_at_q_budget"] is not None else "-"
        out.append(
            f"  {r['rho']:>6.2f} {r['B_effective']:>8.3f} "
            f"{str(r['min_tasks_for_target']):>7} {ceil:>10} "
            f"{str(r['min_participants_at_q_budget']):>9}"
        )
    return "\n".join(out)


def export_rows(claims_rows: dict[str, list[dict]], path: str) -> None:
    """Machine-readable output for the run registry (F-16)."""
    with open(path, "w") as f:
        json.dump(claims_rows, f, indent=2)


# ---------------------------------------------------------------------
# 6. Claim registry
# ---------------------------------------------------------------------

# AUTHOR-FAHMI: one entry per confirmatory claim in F-02. H-P is the sole
# unconditional confirmatory hypothesis; H-E and H-G are readiness-gated and should
# be sized too, marked as conditional. The application contrasts (P1-P0, P2-P1,
# W1-W0, W1-W1-NA) are estimative under F-BLOCK-09 but still need feasibility
# figures — an estimative quantity with an uninformative interval is still a
# planning failure.
CLAIMS: list[Claim] = [
    Claim(
        claim_id="H-P",
        description="Primary confirmatory hypothesis",
        d=0.0, target_power=0.80, alpha=0.05,
        components=VarianceComponents(
            A=0.40, B=0.25, C=0.35,
            source="AUTHOR-FAHMI: replace with attested pilot estimates",
            is_placeholder=True,
        ),
        margin_source="RATIFY",
    ),
    Claim(
        claim_id="H-E",
        description="Evidence readiness hypothesis (conditional)",
        d=0.0, target_power=0.80, alpha=0.05,
        components=VarianceComponents(
            A=0.40, B=0.25, C=0.35,
            source="AUTHOR-FAHMI: replace with attested pilot estimates",
            is_placeholder=True,
        ),
        margin_source="RATIFY",
    ),
    Claim(
        claim_id="H-G",
        description="Governance readiness hypothesis (conditional)",
        d=0.0, target_power=0.80, alpha=0.05,
        components=VarianceComponents(
            A=0.40, B=0.25, C=0.35,
            source="AUTHOR-FAHMI: replace with attested pilot estimates",
            is_placeholder=True,
        ),
        margin_source="RATIFY",
    ),
]


def is_sizeable(claim: Claim) -> bool:
    """A claim can only be sized once its margin and components are real."""
    return (
        claim.d != 0.0
        and not claim.components.is_placeholder
        and not claim.margin_source.upper().startswith("RATIFY")
    )


def run_all(rho_range=None) -> dict[str, dict]:
    """
    Size every claim in the registry.

    Pre-ratification this is expected to report NOT_SIZEABLE for every claim rather
    than failing: the harness exists so that only numbers are missing, and an empty
    result is the honest output when the numbers have not been ratified.
    """
    if not CLAIMS:
        raise ValueError("CLAIMS registry is empty — populate it from F-02.")
    out: dict[str, dict] = {}
    for c in CLAIMS:
        if not is_sizeable(c):
            out[c.claim_id] = {
                "status": "NOT_SIZEABLE — margins/components are unratified placeholders",
                "rows": [],
            }
            continue
        rows = sensitivity_surface(c, rho_range)
        out[c.claim_id] = {"status": demotion_verdict(rows, c), "rows": rows}
    return out


def summary_table(results: dict[str, dict]) -> str:
    lines = [f"  {'claim':<10} {'verdict':<55} {'min_q@rho_max':>14}"]
    for cid, r in results.items():
        min_q = r["rows"][-1]["min_tasks_for_target"] if r["rows"] else "-"
        lines.append(f"  {cid:<10} {r['status']:<55} {str(min_q):>14}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Illustration ONLY. These are power_ceiling.py's placeholder components and
    # arbitrary margins. Nothing here is a sizing decision.
    demo = Claim(
        claim_id="DEMO-not-a-claim",
        description="illustration of harness mechanics; not H-P",
        d=0.30, target_power=0.80, alpha=0.05,
        components=VarianceComponents(A=0.40, B=0.25, C=0.35,
                                      source="power_ceiling placeholders",
                                      is_placeholder=True),
        q_budget=3, p_budget=200,
        margin_source="arbitrary illustration",
    )
    rows = sensitivity_surface(demo)   # uses the declared RHO_RANGE
    print(format_report(demo, rows))
    print(f"  verdict: {demotion_verdict(rows, demo)}")
    print()
    print("Note: q_budget=3 is the current condition-manifest task count (F-12 M-1).")
    print()
    print("REGISTRY STATUS (F-02 claims):")
    print(summary_table(run_all()))
