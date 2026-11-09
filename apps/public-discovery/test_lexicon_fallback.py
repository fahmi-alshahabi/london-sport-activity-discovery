#!/usr/bin/env python3
"""Regression: no unapproved evidence token may reach the public surface.

Found 9 Sep 2026 from Michael's verified pack data. The evidence engine emits exactly three
(evidence_state, grade) pairs — ("T","explicit"), ("T","inherited"), ("U", null) — and `inherited`
has no entry in evidence-language.json. render.phrase()'s old fallback was

    return default or (val or "")

and every call site passes the default "", which is falsy — so an unmapped value fell through to
the RAW INTERNAL TOKEN and rendered "confirmed inherited" on a public page.

Severity ran the opposite way to first reading: the null grade was always SAFE (the
`if a.get("grade")` guard catches it); the non-null unmapped value was the leak, because it passes
that guard and then falls through phrase().

These tests pin the fixed behaviour. They do NOT assert wording for `inherited` — that is content
requiring Clarence's own words and non-author HCI review (C-BLOCK-03), and inventing it in a test
would be the code approving its own copy.
"""
import os, sys, copy, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "server"))
import render  # noqa: E402

REAL_PAIRS = [("T", "explicit"), ("T", "inherited"), ("U", None)]


def test_no_raw_token_ever_reaches_the_surface():
    for cat, val in [("grade", "inherited"), ("grade", "totally_made_up"),
                     ("evidence_state", "Z"), ("terminal_decision", "made_up_decision")]:
        out = render.phrase(cat, val)
        assert out != val, f"phrase({cat!r},{val!r}) echoed the raw internal token"
        assert out == "", f"phrase({cat!r},{val!r}) should drop to empty, got {out!r}"


def test_unmapped_values_are_recorded_not_silently_dropped():
    render.UNMAPPED.clear()
    render.phrase("grade", "inherited")
    assert ("grade", "inherited") in render.UNMAPPED, "a silent drop would hide the gap"


def test_the_three_real_engine_pairs():
    """The two mapped pairs word correctly; the unmapped one loses detail but adds no certainty."""
    render.UNMAPPED.clear()
    got = {}
    for state, grade in REAL_PAIRS:
        st = render.phrase("evidence_state", state)
        gt = render.phrase("grade", grade) if grade else ""
        got[(state, grade)] = f"{st} {gt}".strip()
    assert got[("T", "explicit")] == "confirmed published by the provider"
    assert got[("U", None)] == "not published"          # null grade is guarded — always was
    # inherited: qualifier dropped. Simplification REMOVES detail; it must not ADD certainty.
    assert got[("T", "inherited")] == "confirmed"
    assert "inherited" not in got[("T", "inherited")]
    assert ("grade", "inherited") in render.UNMAPPED


def test_attribute_with_unwordable_state_is_dropped_whole():
    """An evidence state with no approved wording cannot be described honestly, so the attribute
    is not rendered at all — never a predicate id with a blank or raw qualifier."""
    scen = os.path.join(HERE, "server", "scenarios", "supported.json")
    pub = render.load_public("supported")
    assert pub, "fixture should project"
    dec = pub["payload"]["decision"]
    cand = dec["candidates"][0]
    assert cand.get("attributes"), "fixture must carry attributes for this test to mean anything"
    n_before = len(render.build_view(pub)["candidates"][0]["attributes"])

    render.UNMAPPED.clear()
    broken = copy.deepcopy(pub)
    broken["payload"]["decision"]["candidates"][0]["attributes"][0]["evidence_state"] = "Z"
    attrs = render.build_view(broken)["candidates"][0]["attributes"]
    assert len(attrs) == n_before - 1, "the unwordable attribute should be dropped entirely"
    for a in attrs:
        assert a["state_text"], "no attribute may render with an empty state"
        assert a["state_text"] != "Z"
    assert ("evidence_state", "Z") in render.UNMAPPED


def test_real_fixtures_leave_nothing_unmapped():
    """Today's fixtures are fully worded. This fails the day an unworded token starts arriving."""
    render.UNMAPPED.clear()
    for name in ("supported", "indeterminate", "no_match"):
        pub = render.load_public(name)
        if pub:
            render.build_view(pub)
    assert render.UNMAPPED == [], f"unapproved wording reached a view: {render.UNMAPPED}"


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        fn(); print(f"[OK ] {fn.__name__}")
    print("\nRESULT: all lexicon-fallback regressions pass")
