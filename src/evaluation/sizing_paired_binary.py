"""
F-06 — paired binary sizing for the restated H-P.

Sizes the number of TEMPLATES (q) needed for a one-sided paired test of
usefulness, one designated presentation arm vs P0, alpha = .05, power 0.80.

q counts templates, not task rows and not judgments.

Inputs are a declared range, not estimates: no pilot data exists for the
discordant rate, so min-q is reported across a grid as a sensitivity.

Fahmi Alshahabi, 29 August 2026.
Revised 3 September 2026: fixed an iteration defect in the results loop,
named the two z constants, and made the printed output state its own
assumptions. The formula and the grid are unchanged.
"""
import math

# Ratified values, item 6 (19 August 2026): alpha = 0.05, target power = 0.80.
ALPHA = 0.05
POWER = 0.80
Z_ALPHA_ONE_SIDED = 1.645   # z at alpha = 0.05, one-sided
Z_POWER = 0.84              # z at power = 0.80


def min_templates(p_disc, p_fav):
    """p_disc: proportion of templates where the arms disagree.
       p_fav:  of those, proportion favouring the designated arm."""
    n_disc = ((Z_ALPHA_ONE_SIDED * 0.5 + Z_POWER * math.sqrt(p_fav * (1 - p_fav))) / (p_fav - 0.5)) ** 2
    q_min = n_disc / p_disc
    return math.ceil(q_min)


p_disc_values = [0.20, 0.30, 0.40, 0.50]
p_fav_values = [0.60, 0.65, 0.70, 0.75, 0.80]

print("F-06 sizing — one-sided paired binary test, designated arm vs P0")
print("alpha =", ALPHA, "(one-sided); target power =", POWER)
print("q counts task_template_id, not task rows and not judgments")
print("p_disc = share of templates where the arms disagree")
print("p_fav  = of those, share favouring the designated arm")
print()
print("min templates (q) by discordant rate and favourable share")
print("p_disc", p_fav_values)
for p_disc in p_disc_values:
    print(p_disc, [min_templates(p_disc, p_fav) for p_fav in p_fav_values])
