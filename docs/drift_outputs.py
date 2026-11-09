"""This script is for loading and inspecting any outputs from drift_analysis.py"""

import pandas as pd

# Loads the drift results
drift = pd.read_csv("drift_2026-08-27_2026-09-06.csv")  # Change this line to the chosen output from the drift_analysis.py

# Extract the feed type from the feed ID. Feed IDs use "--" to separate the provider/feed name from its type.
# For example: "provider--sessionseries" -> "sessionseries".
drift["feed_type"] = drift["feed_id"].str.split("--").str[-1]

# Count each type of change (e.g. unchanged, added, removed) separately for each feed type.
by_type = drift.groupby("feed_type")["change"].value_counts().unstack(fill_value=0)

# Calculate persistence as the percentage of records that remained unchanged between the two snapshots.
by_type["persistence"] = (by_type.get("unchanged", 0) / by_type.sum(axis=1) * 100).round(1)

# Show the persistence percentage for each feed type, from lowest to highest.
print(by_type[["persistence"]].sort_values("persistence"))

print("\nfull breakdown:")
print(by_type)