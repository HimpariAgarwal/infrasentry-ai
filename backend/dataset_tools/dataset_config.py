
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dataset directories
DATASET_ROOT = PROJECT_ROOT / "data" / "raw" / "RDD2022"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Supported image formats
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}

# RDD2022 damage classes
DAMAGE_CLASSES = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole"
}

# Dataset countries
COUNTRIES = [
    "India",
    "Japan",
    "Czech",
    "Norway",
    "United_States",
    "China_MotorBike",
    "China_Drone"
]

# Output files
MANIFEST_FILE = PROCESSED_DIR / "rdd2022_manifest.csv"
REPORT_FILE = PROCESSED_DIR / "rdd2022_validation_report.json"
