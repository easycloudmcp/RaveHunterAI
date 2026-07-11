from pathlib import Path

APP_NAME = "RaveHunter AI"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = BASE_DIR / "ravehunter.db"

COLLECTORS = [
    "instagram",
    "resident_advisor",
    "shotgun",
    "dice",
    "ticketio",
]

COUNTRIES = [
    "Germany",
    "Austria",
    "Switzerland",
    "Italy",
]

HOME_CITY = "Munich"