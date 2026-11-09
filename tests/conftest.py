import sys
from pathlib import Path

# Make the evaluation modules (src/evaluation) importable from the tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "evaluation"))
