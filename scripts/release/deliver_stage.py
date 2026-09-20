"""deliver に渡す入力 (ストア情報・年齢制限・審査情報) を build/deliver に用意する。"""
import json
import shutil
from pathlib import Path

from . import paths
from .settings import load_settings
from .store_rules import read_field

METADATA_FIELDS = ["name", "subtitle", "description", "keywords", "promotional_text", "privacy_url", "support_url"]


def stage_metadata(metadata_dir: Path, out_dir: Path) -> list:
    """空でない項目だけを deliver の形式 (<dir>/ja/*.txt) にコピーする。空の項目を送ると既存の値を消しうるため。"""
    target = Path(out_dir) / "metadata" / "ja"
    if target.parent.exists():
        shutil.rmtree(target.parent)
    target.mkdir(parents=True)
    written = []
    for field in METADATA_FIELDS:
        text = read_field(metadata_dir, field)
        if text:
            (target / f"{field}.txt").write_text(text, encoding="utf-8")
            written.append(field)
    return written


def review_information(settings: dict, contact_file: Path):
    """審査情報。連絡先ファイルが無い・不完全なら None (提出前の検査で止まる)。"""
    contact_file = Path(contact_file)
    if not contact_file.exists():
        return None
    contact = json.loads(contact_file.read_text(encoding="utf-8"))
    fields = ["first_name", "last_name", "phone_number", "email_address"]
    if any(not str(contact.get(f, "")).strip() for f in fields):
        return None
    app_store = settings["app_store"]
    info = {f: contact[f] for f in fields}
    info.update({
        "demo_account_required": app_store["demo_account_required"],
        "demo_user": "",
        "demo_password": "",
        "notes": app_store.get("review_notes", ""),
    })
    return info


def stage_deliver(out_dir: Path = paths.DELIVER_DIR, settings_file: Path = paths.SETTINGS_FILE,
                  metadata_dir: Path = paths.METADATA_DIR, contact_file: Path = paths.REVIEW_CONTACT_FILE) -> dict:
    settings = load_settings(settings_file)
    out_dir = Path(out_dir)
    written = stage_metadata(metadata_dir, out_dir)

    (out_dir / "app_rating.json").write_text(
        json.dumps(settings["app_store"]["age_rating"], indent=2), encoding="utf-8")

    review = review_information(settings, contact_file)
    review_path = out_dir / "review_information.json"
    if review is not None:
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    elif review_path.exists():
        review_path.unlink()

    app_store = settings["app_store"]
    options = {
        "metadata_path": str(out_dir / "metadata"),
        "app_rating_config_path": str(out_dir / "app_rating.json"),
        "review_information_path": str(review_path) if review is not None else None,
        "primary_category": app_store["primary_category"],
        "price_tier": app_store["price_tier"],
        "copyright": settings["copyright"],
        "uses_non_exempt_encryption": app_store["uses_non_exempt_encryption"],
        "fields": written,
    }
    (out_dir / "options.json").write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding="utf-8")
    return options
