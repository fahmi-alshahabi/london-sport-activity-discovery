"""C-08 deterministic intent parser (WP §9).

AI-ASSISTED SCAFFOLD. NOT authorship evidence. The conversational layer may interpret and communicate;
it does NOT decide what is true (WP §9.1). This parser is deterministic and closed-vocabulary: it
never guesses — an unrecognised or incomplete query routes to parse_clarification, never to a
fabricated result. An LLM parser can later replace this behind the same typed-intent contract
(constrained decoding), but the discipline demonstrated here does not depend on a model.
"""
from __future__ import annotations
import re

ACTIVITIES = {"swimming": "swimming", "swim": "swimming",
              "climbing": "climbing", "climb": "climbing",
              "yoga": "yoga"}
BOROUGHS = {"croydon": "LB Croydon", "havering": "LB Havering"}
ACCESS_TERMS = ("step-free", "step free", "stepfree", "wheelchair")

# recognised (activity, borough) -> the shared frozen scenario / DecisionEnvelope
SCENARIO_MAP = {
    ("swimming", "LB Croydon"): "supported",
    ("climbing", "LB Havering"): "no_match",
    ("yoga", "LB Croydon"): "indeterminate",
}

# A negation must never be read as a positive requirement (MS-9, Michael 2026-08-23):
# "not wheelchair accessible" must NOT become "requires step-free".
NEG_ACCESS_RE = re.compile(
    r"\binaccessible\b|"
    r"\b(?:not|no|without|non[-\s]?)\s+(?:\w+\s+){0,2}?(?:step[-\s]?free|stepfree|wheelchair|accessible)\b",
    re.I)
# A stated price ceiling cannot be evaluated from the demonstration evidence; it must be surfaced,
# never silently dropped (MS-9).
PRICE_RE = re.compile(
    r"£\s*\d+|\b\d+\s*(?:pounds|quid|gbp)\b|\bunder\s+£?\s*\d+\b|\bless\s+than\s+£?\s*\d+\b",
    re.I)


def parse(text: str) -> dict:
    t = (text or "").lower()
    activity = None
    for k, v in ACTIVITIES.items():
        if re.search(rf"\b{k}\b", t):
            activity = v
            break
    borough = None
    for k, v in BOROUGHS.items():
        if re.search(rf"\b{k}\b", t):
            borough = v
            break
    unsupported = []
    neg_access = bool(NEG_ACCESS_RE.search(t))
    if neg_access:
        access = None                                    # never reverse a negation (MS-9)
        unsupported.append("negated accessibility constraint")
    elif any(a in t for a in ACCESS_TERMS):
        access = "step_free"
    else:
        access = None
    if PRICE_RE.search(t):
        unsupported.append("price")                      # stated but not evaluable from the evidence (MS-9)

    hard = []
    if activity:
        hard.append(f"activity={activity}")
    if access:
        hard.append(f"access={access}")
    ambiguous = []
    if not activity:
        ambiguous.append("activity")
    if not borough:
        ambiguous.append("area")

    # Every demonstration fixture assumes step-free access; only resolve one when the user actually
    # asked for step-free, otherwise we would answer a different (step-free) query than posed (MS-9).
    base = SCENARIO_MAP.get((activity, borough))
    scenario = base if (base and access == "step_free") else None
    if base and access is None and not neg_access:
        ambiguous.append("step-free access requirement")

    return {
        "activity": activity, "borough": borough, "access": access,
        "hard": hard, "ambiguous": ambiguous, "unsupported": unsupported, "scenario": scenario,
        "confident": bool(activity and borough and scenario) and not unsupported,
        "high_consequence": access is not None,  # accessibility is a high-consequence constraint (WP §9.2)
    }
