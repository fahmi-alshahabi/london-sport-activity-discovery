"""
Drift analysis between two clean snapshots.

Handles the three artifacts that broke the naive version:
1. Feeds joining/leaving --> restrict item-level drift to COMMON feeds
2. Date-stamped slot/session ids --> strip the trailing date so the same recurring slot isn't counted as churn every period
3. Provider renames --> reported as FEED-level drift, kept out of item-level churn

Reports TWO levels, kept distinct (the lesson from the denominator collisions):
- Feed-level drift : which feeds/providers appeared or disappeared
- Item-level drift : for feeds that existed in both snapshots, which activities appeared, disappeared, changed, or stayed the same
"""
import json, re, hashlib
from pathlib import Path
from collections import defaultdict
import pandas as pd

# Set these to the two snapshots you want comparisons between 
SNAP_A = "2026-08-27"
SNAP_B = "2026-09-06"
SNAP_ROOT = Path("../notebooks/snapshots")   # adjust if your snapshots live elsewhere

# RegEx for date normalisation.
_DATE_SUFFIX = re.compile(r"[_/-]?\d{4}-\d{2}-\d{2}[T_]\d{2}[-:]\d{2}([-:]\d{2})?.*$")

# Function for using the above RegEx. Used for when two activities have the same name, but the date suffix differs differentiating old and new activities
def stable_id(item_id):
    # Remove a trailing date-stamp so a recurring slot keeps one identity across vintages
    return _DATE_SUFFIX.sub("", str(item_id))

# Function for loading snapshots. Reducing the each record (from data acquisition/reconstruction) to feed ID, kind, and hash of its data
def load_state(snap):
    path = SNAP_ROOT / snap / "records.jsonl"
    # Create storage structures for state and feeds
    state = {}      # Stores information about every item
    feeds = set()   # Set is used here because we only care about if a feed exists, not how many records it contains
    with open(path, encoding="utf-8") as f:
        # Makes each line of the output represent one JSON object
        for line in f:
            r = json.loads(line)
            
            # Record the feed
            fid = r.get("feed_id")
            feeds.add(fid)
            
            # Create a stable ID. So for example, ABC123_2026-08-15T07-00-00 would become ABC123
            sid = stable_id(r["item_id"])
            
            # Create a hash of the data using SHA256    
            dh = hashlib.sha256(
                json.dumps(r.get("data"), sort_keys=True, ensure_ascii=False).encode()  # Convert the python object back into JSON text
            ).hexdigest()
            state[(fid, sid)] = (fid, r.get("kind"), dh)   # key includes feed to avoid cross-feed id clashes
    return state, feeds


def main():
    # Load the older snapshot
    print(f"Loading {SNAP_A} ...")
    a, feeds_a = load_state(SNAP_A)
    print(f"  {len(a):,} items, {len(feeds_a)} feeds")  # Print how many items and feeds were found in the older snapshot (A)
    
    # Load the newer snapshot
    print(f"Loading {SNAP_B} ...")
    b, feeds_b = load_state(SNAP_B)
    print(f"  {len(b):,} items, {len(feeds_b)} feeds")  # Same print equivalent for the newer snapshot (B)

    # feed-level drift 
    left = sorted(feeds_a - feeds_b)    # Feeds that existed in A but not B. The feeds that left
    joined = sorted(feeds_b - feeds_a)  # Feeds that exist in B but didn't exist in A. These are the feeds that joined
    common = feeds_a & feeds_b          # The intersection between A & B. These are common feeds
    # Print the outputs 
    print("\n=== FEED-LEVEL DRIFT ===")
    print(f"  feeds in {SNAP_A}: {len(feeds_a)} | in {SNAP_B}: {len(feeds_b)} | shared: {len(common)}")
    print(f"  LEFT  (in {SNAP_A} only): {len(left)}")
    for x in left[:20]: print(f"      - {x}")
    print(f"  JOINED (in {SNAP_B} only): {len(joined)}")
    for x in joined[:20]: print(f"      + {x}")
    print("  NOTE: a renamed provider shows as one LEFT + one JOINED, inspect the lists.")

    # item-level drift, restricted to common feeds. The following code removes items belonging to only one of the feeds.
    a_common = {k: v for k, v in a.items() if v[0] in common}
    b_common = {k: v for k, v in b.items() if v[0] in common}
    a_keys, b_keys = set(a_common), set(b_common)   # Get all item keys

    rows = []   # Each item comparison will eventually become one row in this list
    for key in a_keys | b_keys:     # Compares every item that appears in either snapshot
        in_a, in_b = key in a_common, key in b_common
        # Following if statements are used to classify the change as "disappeared", "appeared", "modified", or "unchanged"
        if in_a and not in_b:              
            change = "disappeared"
        elif in_b and not in_a:            
            change = "appeared"
        elif a_common[key][2] != b_common[key][2]: 
            change = "modified"
        else:                              
            change = "unchanged"
        src = b_common.get(key) or a_common.get(key)    # Retrieves the stored information about the item
        rows.append({"feed_id": src[0], "kind": src[1], "change": change})  # Add the results

    # Turn the results into a DF and save it as a CSV
    drift = pd.DataFrame(rows)  
    drift.to_csv(f"drift_{SNAP_A}_{SNAP_B}.csv", index=False)

    # Print the overall item-level results
    print(f"\n=== ITEM-LEVEL DRIFT (common feeds, date-normalised ids) ===")
    print(f"  {len(drift):,} distinct items over {len(common)} shared feeds")
    # Counts each type of change and prints it
    print(drift["change"].value_counts())   
    # Calculate persistence
    total = len(drift)
    unchanged = (drift["change"] == "unchanged").sum()
    print(f"\n  persistence (unchanged): {unchanged/total:.1%}")    # Unchanged tells us how many items persisted without modification
    print(f"  churn (appeared+disappeared+modified): {(total-unchanged)/total:.1%}")    # Calculate churn. Anything that isn't unchanged is considered churn

    # Find the feeds with the most churn
    print("\n  Top churning feeds:")
    churn = drift[drift.change != "unchanged"].groupby("feed_id").size().sort_values(ascending=False)
    print(churn.head(10))


if __name__ == "__main__":
    main()
