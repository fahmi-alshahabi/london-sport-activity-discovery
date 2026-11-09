# This script is for testing between differing questioning strategies aka E0-E4

import random, copy
from d5_preference_model import PreferenceBelief, preference_score, DIMENSIONS

# E0 baseline: do not ask the user any clarification question.
def e0_null(belief, asked, **kw): return None

# E1 baseline: ask preference dimensions in a fixed predetermined order, skipping dimensions that have already been asked.
_FIXED = ["activity", "day_type", "time"]
def e1_fixed(belief, asked, **kw):
    for d in _FIXED:
        if d not in asked: return d
    return None

# E2 baseline: randomly choose one of the preference dimensions that has not already been asked.
def e2_random(belief, asked, rng=None, **kw):
    rng = rng or random
    rem = [d for d in belief.probs if d not in asked]
    return rng.choice(rem) if rem else None

# E3 chooses the unasked dimension with the highest entropy, i.e. the preference dimension where the current belief is most uncertain.
def e3_max_entropy(belief, asked, **kw):
    rem = [d for d in belief.probs if d not in asked]
    return max(rem, key=lambda d: belief.entropy(d)) if rem else None

# Helper function for E4 EVOI
# Essentially asks, given what we currently believe about the user's preferences, how good is the best available candidate?
def _decision_quality(belief, candidates):
    """Quality of the current best decision = preference score of the top candidate."""
    if not candidates:  # If there are no candidates, then the decision quality is 0
        return 0.0
    # Calculates the preference score for every candidate and returns the highest ones
    return max(preference_score({d: c.get(d) for d in DIMENSIONS if c.get(d) is not None}, belief)
               for c in candidates)

# Function used by E4 to ask hypothetical questions. Essentially, what would our belief look like if the user answered X.
def _belief_after(belief, dim, answer):
    b2 = PreferenceBelief(probs=copy.deepcopy(belief.probs))    # Creates new belief object based on the current probabilities
    b2.update(dim, answer)  # Apply the Bayesian update for the hypothetical answer
    return b2

# E4 the Expected Value of Information (EVOI). Asks, which question is expected to improve the final recommendation the most.
def e4_evoi(belief, asked, candidates=None, cost=0.0, **kw):
    # Finds unanswered dimensions that haven't been asked
    rem = [d for d in belief.probs if d not in asked]
    if not rem:     # If everything has already been asked, return None
        return None
    
    
    if not candidates:
        return max(rem, key=lambda d: belief.entropy(d))   # if it can't compute EVOI entropy fallback to E3
    
    # disc = dimensions that are discriminative between candidates
    # E4 only considers a dimension if the candidates actually differ between the candidates
    disc = [d for d in rem
            if len({c.get(d) for c in candidates if c.get(d) is not None}) > 1]
    if not disc:    # If all candidates are the same, return None
        return None
    
    
    current_q = _decision_quality(belief, candidates) # Current decision quality (baseline)
    best_dim, best_evoi = None, float("-inf")   # Tracks the best question
    for d in disc:      # Evaluate every possible question. For each dimension, calculate the expected quality after asking that question
        expected_q = 0.0
        for answer, p_answer in belief.probs[d].items():    # Consider all possible answers
            if p_answer <= 0:   # Ignores impossible answers
                continue
            expected_q += p_answer * _decision_quality(_belief_after(belief, d, answer), candidates) # Calculate the expected recommendation quality
        evoi = expected_q - current_q - cost
        if evoi > best_evoi:    # Keep the question with the highest EVOI score
            best_evoi, best_dim = evoi, d
    return best_dim if best_evoi > 0 else None

# Dictionary of the different strategies mapped to their respective functions
STRATEGIES = {"E0_null":e0_null,"E1_fixed":e1_fixed,"E2_random":e2_random,
              "E3_max_entropy":e3_max_entropy,"E4_evoi":e4_evoi}

if __name__ == "__main__":
    # Create an initial belief. The following essentially says category has already been asked.
    b = PreferenceBelief(); b.update("category","swim"); asked={"category"}
    
    # Creates example candidates. Three hypothetical activities.
    cands = [{"category":"swim","day_type":"weekday","time":"morning"},
             {"category":"swim","day_type":"weekend","time":"morning"},
             {"category":"swim","day_type":"weekend","time":"afternoon"}]
    rng = random.Random(42)
    
    # Print the outputs
    print("belief:", b.summary(), "\nasked:", asked, "\n") 
    for name,fn in STRATEGIES.items():
        print(f"  {name:16s} -> {fn(b, asked, candidates=cands, rng=rng)}")