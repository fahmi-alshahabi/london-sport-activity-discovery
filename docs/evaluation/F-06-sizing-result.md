# F-06 — sizing result for the restated H-P

**Owner:** Fahmi Alshahabi
**Run date:** 2026-09-03
**Script:** `src/evaluation/sizing_paired_binary.py` — branch `fahmi/proposal-v2-sections-6-7`, 
**How run:** executed in Google Colab on 2026-09-03, output below is verbatim

## Assumptions

- One-sided paired binary test of usefulness, designated presentation arm vs P0
- alpha = 0.05 one-sided, target power = 0.80 (ratified, item 6, 19 August 2026)
- q counts `task_template_id`, not task rows and not judgments
- `p_disc` = share of templates where the arms disagree; `p_fav` = of those, share favouring the designated arm

## Output

```
F-06 sizing — one-sided paired binary test, designated arm vs P0
alpha = 0.05 (one-sided); target power = 0.8
q counts task_template_id, not task rows and not judgments
p_disc = share of templates where the arms disagree
p_fav  = of those, share favouring the designated arm

min templates (q) by discordant rate and favourable share
p_disc [0.6, 0.65, 0.7, 0.75, 0.8]
0.2 [762, 333, 183, 113, 75]
0.3 [508, 222, 122, 76, 50]
0.4 [381, 167, 92, 57, 38]
0.5 [305, 133, 73, 46, 30]
```


## Not covered

The discordant rate is undetermined — no pilot data exists for it, so the
table above is a declared sensitivity grid across a plausible range, not an
estimate of required q. The 30 corner is the most optimistic cell in the grid
and is not a target.

## SIGN-OFF — F-06 sizing result

- **Claim ID:** F-06-sizing
- **Artefacts checked:** `src/evaluation/sizing_paired_binary.py` — branch `fahmi/proposal-v2-sections-6-7`, commit `4f8333d
`
- **Method:** ran it in Colab on 3 Sep.
- **Outcome:** APPROVED
- **Conditions:** [if any]
- **Not covered by this sign-off:** [the discordant rate is undetermined; this sign-off covers the sizing computation only, not the authoring count decision]
- **Reference:** CA-01.A9
- **Signed:** Fahmi Alshahabi · 2026-09-03
