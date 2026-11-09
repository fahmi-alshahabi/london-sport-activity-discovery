"""Takes the 5 question strategies (E0-E5) from d5_question_strategies.py and put 
them through the same simulated user scenarios, and measure how well each perform."""

import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d5_preference_model import PreferenceBelief, DIMENSIONS, preference_score
from d5_question_strategies import STRATEGIES

#This class represents a fake user. It's built in a way where the simulator has a hidden "true" 
#preference that the strategies don't know directly. They have to discover it by asking questions
class SimulatedUser:
    def __init__(self, rng):
        self.true_pref = {dim: rng.choice(vals) for dim,vals in DIMENSIONS.items()}
    
    # Function for simulated users answering a question
    def answer(self, dim): 
        return self.true_pref.get(dim)  # Returns the user's hidden true preference for the specific dimension
    
    # Function for how the simulator decides whether the final recommendation was actually correct
    # It compares the chosen candidate against the user's true preferences
    def is_good_match(self, facets):
        return all(facets.get(k) == self.true_pref.get(k) for k in ["activity", "day_type", "time"])

# Function for creating a pool of activities from which the system will eventually recommend one.
# By default n = 40, meaning each simulated user gets a pool of 40 candidates
def make_pool(rng, n=40):
    # Each generated candidate gets an ID and is randomly assigned values for each dimension.
    return [{"item_id":f"c{i}", **{d: rng.choice(v) for d,v in DIMENSIONS.items()}} for i in range(n)]  

# Function for running one complete interaction between one strategy, one simulated user, and one candidate pool.
def run_episode(fn, user, pool, rng, max_q=3):
    belief = PreferenceBelief()     # The strategies current beliefs about the user
    asked = set()   # asked = a set containing the preference dimensions that have already been asked
    nq = 0      # nq = Number of questions asked
    
    
    for _ in range(max_q):
        # fn represents the current question strategy being used (E0-E4)
        dim = fn(belief, asked, candidates=pool, rng=rng)
        # dim returns None when there are no more questions to ask. For example, in E0 it will always return None.
        if dim is None: 
            break
        belief.update(dim, user.answer(dim))    # Updates the Bayesian belief model with the answer to the specific dimension
        asked.add(dim)  # Add to the asked set the dimension that was asked
        nq += 1     # Increment the number of questions asked by 1
    
    # Once questioning is finished, this chooses the candidate with the highest preference score according to the current belief.
    top = max(pool, key=lambda c: preference_score(c, belief))      # Chooses the candidate with the highest score using the max function
    return {"questions":nq, "matched":user.is_good_match(top)}      # Returns number of questions asked and whether it matched.


# Function for running the actual simulation with a default 500 simulated users, a default random seed for reproducibility, and a default max 4 questions per user.
def run_simulation(n_users=500, seed=42, max_questions=4):
    res = {n:{"matched":0,"questions":0} for n in STRATEGIES}   # Instantiates res which will hold the results
    
    # Loop to run and evaluate through each question strategy (E0-E4)
    for name, fn in STRATEGIES.items():  
        rng = random.Random(seed)   # Resets the random generator, meaning each iteration has the same starting underlying sequence of simulated randomness
        
        # Loop through the number of users. For each user, create a random simulated user and a random pool of 40 activities.
        for _ in range(n_users):    
            u = SimulatedUser(rng)
            pool = make_pool(rng)
            ep = run_episode(fn,u,pool,rng,max_questions)   # Run the episode, refer to the function above at line 31
            res[name]["matched"]+=ep["matched"]
            res[name]["questions"]+=ep["questions"]
    print(f"D5 simulation — {n_users} seeded users (seed={seed}), max {max_questions} q\n")     # Prints the experimental description
    
    # For reference, the text after : in each {} (e.g., 'strategy':16s)
    # are just for clean formatting and was selected through testing and manually seeing if the output table looked clean
    print(f"  {'strategy':16s} {'match rate':>11s} {'avg questions':>14s} {'match/q':>10s}")    # Prints the table headings
    print("  "+"-"*54)
    for name,r in res.items():
        mr = r["matched"]/n_users       # Calculates the match rate. What % of simulated users received correct matches
        aq = r["questions"]/n_users     # Calculates the average question. How many questions did the strategy ask on average per user?
        eff = mr / aq if aq else 0      # Calculates match rate per question asked. This calculates the efficiency.
        print(f"  {name:16s} {mr:>10.1%} {aq:>14.2f} {eff:>10.3f}")     # Print the results
    return res


if __name__ == "__main__":
    r1 = run_simulation(500,42,3)       # Runs the first simulation
    print("\n=== reproducibility check (same seed) ===")
    r2 = run_simulation(500,42,3)       # Runs the second simulation
    print(f"\nidentical: {all(r1[k]==r2[k] for k in r1)}")
    print("\n=== tighter budget (2 q) — where strategy choice matters ===")
    run_simulation(500,42,2)        # Runs the third simulation
