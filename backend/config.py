# Configuration for NEUROFRAME-X
import os

# Choose the action model: "epic" for EPIC‑KITCHENS TSM, "r3d18" for the baseline.
# Can be overridden with the environment variable ACTION_MODEL.
ACTION_MODEL = os.getenv("ACTION_MODEL", "r3d18").lower()

# Helper flag indicating whether EPIC model should be used.
USE_EPIC_MODEL = ACTION_MODEL == "epic"
