"""リリース自動化が参照するファイルの置き場所。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STORE_DIR = ROOT / "store"
SETTINGS_FILE = STORE_DIR / "settings.json"
LOCAL_SETTINGS_NAME = "settings.local.json"
METADATA_DIR = STORE_DIR / "metadata" / "ja"
PRIVACY_DETAILS_FILE = STORE_DIR / "app_privacy_details.json"
NAME_CANDIDATES_FILE = STORE_DIR / "name_candidates.txt"
REVIEW_CONTACT_FILE = STORE_DIR / "review_contact.local.json"
REVIEW_CONTACT_EXAMPLE = STORE_DIR / "review_contact.example.json"
SCREENSHOTS_DIR = STORE_DIR / "screenshots" / "ja"

ICON_SET_DIR = ROOT / "HouseholdApp" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset"

BUILD_DIR = ROOT / "build"
STATE_FILE = BUILD_DIR / "release_state.json"
DELIVER_DIR = BUILD_DIR / "deliver"
LOG_DIR = BUILD_DIR / "logs"
