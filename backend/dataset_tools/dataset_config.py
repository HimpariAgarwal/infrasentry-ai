
from pathlib import Path

# ==========================================
# PROJECT DIRECTORIES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "data" / "raw" / "RDD2022"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ==========================================
# IMAGE FORMATS
# ==========================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}


# ==========================================
# FOUR-CLASS BASELINE
# ==========================================

DAMAGE_CLASSES = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole",
}

# Stable numeric IDs for the baseline model.
CLASS_TO_ID = {
    "D00": 1,
    "D10": 2,
    "D20": 3,
    "D40": 4,
}

ID_TO_CLASS = {
    value: key
    for key, value in CLASS_TO_ID.items()
}


# ==========================================
# ADDITIONAL KNOWN RDD2022 CLASSES
# ==========================================

EXTENDED_DAMAGE_CLASSES = {
    "D01": "Longitudinal Construction Joint Crack",
    "D11": "Transverse Construction Joint Crack",
    "D43": "Blurred Crosswalk",
    "D44": "Blurred White Lane Marking",
    "D50": "Manhole",
}

# All known classes, including the four baseline classes.
KNOWN_DAMAGE_CLASSES = {
    **DAMAGE_CLASSES,
    **EXTENDED_DAMAGE_CLASSES,
}

# These classes are preserved in the original annotations
# but excluded from the four-class baseline.
EXCLUDED_FROM_BASELINE_CLASSES = set(
    EXTENDED_DAMAGE_CLASSES.keys()
)

# Observed label requiring manual investigation.
# Never automatically convert it into another class.
UNRESOLVED_LABELS = {
    "D0w0",
}


# ==========================================
# DATASET COUNTRIES
# ==========================================

COUNTRIES = [
    "India",
    "Japan",
    "Czech",
    "Norway",
    "United_States",
    "China_MotorBike",
    "China_Drone",
]


# ==========================================
# OUTPUT FILES
# ==========================================

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_FILE = PROCESSED_DIR / "rdd2022_manifest.csv"

REPORT_FILE = PROCESSED_DIR / "rdd2022_validation_report.json"
