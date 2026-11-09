"""D5 (+ D4 final stage) Bayesian preference model. Belief over preference dimensions;
updates on each answer; exposes entropy (for strategies) and preference_score (for D4)."""
from dataclasses import dataclass, field
import math

# Define the dimensions. These are the 3 things the system
# is interested in knowing about the user's preferences.
DIMENSIONS = {
    "activity": ["swim", "fitness suite", "group exercise", "junior", "leisure pool"],
    "day_type": ["weekday", "weekend"],
    "time": ["morning", "afternoon", "evening"],
}

# Instantiate the class Preference Belief. Its job is to store the system's current belief about what the user wants.
@dataclass
class PreferenceBelief:
    probs: dict = field(default_factory=dict)
    
    # Creating the initial belief. Done using uniform priors
    # Uniform priors = We don't know what the user prefers, so assign equal probability to each possible answer.
    def __post_init__(self):
        if not self.probs:
            for dim,vals in DIMENSIONS.items():
                self.probs[dim] = {v:1.0/len(vals) for v in vals}
                
    # Function for updating the belief after the user gives new info.
    # confidence = 0.85 essentially gives the stated answer a likelihood of 0.85, and the remaining 0.15 is distributed amongst other possible values
    def update(self, dim, stated_value, confidence=0.85):
        if dim not in self.probs:
            raise ValueError(
                f"Unknown preference dimension: {dim!r}. "
                f"Expected one of: {list(self.probs)}"
    )   # Prevents updates from unknown dimensions
        # get possible values of the dimension, counts the alternative, and creates the posterior
        vals = list(self.probs[dim]) 
        n_other = len(vals)-1
        post = {}  
        for v in vals:  
            prior = self.probs[dim][v]
            like = confidence if v==stated_value else (1-confidence)/max(1,n_other)
            post[v] = prior*like    # Bayesian core, essentially new belief = old belief x how compatible the new evidence is with that value
        tot = sum(post.values()) or 1.0     # Normalise the probabilities so that they add up to 1
        self.probs[dim] = {v:p/tot for v,p in post.items()}
    
    # Function for getting what the model currently thinks is the user's most likely preference for the inputted dimension
    def most_likely(self, dim):
        d = self.probs[dim]
        v = max(d,key=d.get)
        return v,d[v]
    
    # Essentially E3 of my d5_question_strategies.py file and essentially calculates entropy. Entropy relates to the uncertainty.
    def entropy(self, dim):
        return -sum(p*math.log2(p) for p in self.probs[dim].values() if p>0)
    
    # Function for calculating the total uncertainty across all preference dimensions
    def total_uncertainty(self):
        return sum(self.entropy(d) for d in self.probs)
    
    # Function for making human-readable summary of the current belief
    def summary(self):
        return " | ".join(f"{d}: {self.most_likely(d)[0]} ({self.most_likely(d)[1]:.0%}, H={self.entropy(d):.2f})" for d in self.probs)

# Function for getting a preference score. Essentially, given what we currently believe the user wants, how well does this particular activity match those preferences?
def preference_score(card_facets, belief):
    """
    Score a card against the fixed preference dimensions.

    Missing or unrecognised facets are not removed from the denominator.
    Instead, they contribute the uniform prior mass for that dimension.

    This makes missing metadata neutral rather than rewarding it.
    """

    scores = []

    for dim, values in DIMENSIONS.items():

        facet_value = card_facets.get(dim)

        if (
            facet_value is not None
            and dim in belief.probs
            and facet_value in belief.probs[dim]
        ):
            scores.append(
                belief.probs[dim][facet_value]
            )

        else:
            # Missing / unrecognised evidence contributes
            # the uniform prior mass for this dimension.
            scores.append(
                1.0 / len(values)
            )

    return sum(scores) / len(scores)

if __name__ == "__main__":
    b = PreferenceBelief()  # Instantiates a neutral belief 
    print("PRIOR:", b.summary(), f"| H={b.total_uncertainty():.2f}")    # Print the initial state
    for dim,val,say in [("activity","swim","swimming"),("day_type","weekend","weekend"),("time","morning","morning")]:  # Simulates 3 user answers
        b.update(dim,val); print(f"after '{say}':", b.summary(), f"| H={b.total_uncertainty():.2f}")
    # Print outputs for the comparison of 2 user activity examples
    print(
        "score swim/wknd/am:",
        round(
            preference_score(
                {
                    "activity": "swim",
                    "day_type": "weekend",
                    "time": "morning"
                },
                b
            ),
            3
        )
    )

    print(
        "score gym/wkdy/pm:",
        round(
            preference_score(
                {
                    "activity": "fitness suite",
                    "day_type": "weekday",
                    "time": "evening"
                },
                b
            ),
            3
        )
    )
