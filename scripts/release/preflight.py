"""審査提出の前提条件 (アイコン・審査連絡先・URL) の検査。"""
import json
import struct
from pathlib import Path

from . import paths
from .store_rules import read_field

ICON_SIZE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CONTACT_FIELDS = ["first_name", "last_name", "phone_number", "email_address"]
URL_FIELDS = ["privacy_url", "support_url"]


def check_icon(icon_set_dir: Path) -> list:
    """AppIcon.appiconset に 1024x1024 の PNG (透過なし) が登録されているか。"""
    where = "HouseholdApp/Resources/Assets.xcassets/AppIcon.appiconset"
    contents = Path(icon_set_dir) / "Contents.json"
    filename = None
    if contents.exists():
        for image in json.loads(contents.read_text(encoding="utf-8")).get("images", []):
            if image.get("filename"):
                filename = image["filename"]
                break
    if filename is None:
        return [f"アプリアイコン — {where} に 1024x1024 の PNG を置き、Contents.json の images に filename を追記してください"]

    icon_path = Path(icon_set_dir) / filename
    if not icon_path.exists():
        return [f"アプリアイコン — {where}/{filename} がありません"]

    header = icon_path.read_bytes()[:26]
    if len(header) < 26 or header[:8] != PNG_SIGNATURE:
        return [f"アプリアイコン — {where}/{filename} が PNG ではありません"]
    width, height = struct.unpack(">II", header[16:24])
    color_type = header[25]
    problems = []
    if (width, height) != (ICON_SIZE, ICON_SIZE):
        problems.append(f"アプリアイコン — {filename} が {width}x{height} です (1024x1024 が必要)")
    if color_type in (4, 6):
        problems.append(f"アプリアイコン — {filename} に透過 (アルファチャンネル) があります (App Store は不可)")
    return problems


def check_review_contact(contact_file: Path, example_file: Path) -> list:
    """審査連絡先 (Git 管理外のローカルファイル) が揃っているか。"""
    where = "store/review_contact.local.json"
    if not Path(contact_file).exists():
        return [f"審査連絡先 — {where} がありません。{Path(example_file).name} を {Path(contact_file).name} にコピーして入力してください"]
    data = json.loads(Path(contact_file).read_text(encoding="utf-8"))
    return [
        f"審査連絡先 — {where} の \"{field}\" が未入力です"
        for field in CONTACT_FIELDS
        if not str(data.get(field, "")).strip()
    ]


def check_urls(metadata_dir: Path) -> list:
    """プライバシーポリシー URL とサポート URL が入力済みか。"""
    problems = []
    for field in URL_FIELDS:
        value = read_field(metadata_dir, field)
        where = f"store/metadata/ja/{field}.txt"
        if not value:
            problems.append(f"{field} — {where} に URL を1行で入力してください")
        elif not value.startswith(("http://", "https://")):
            problems.append(f"{field} — {where} は http(s):// で始まる URL にしてください")
    return problems


def check_submit(
    icon_set_dir: Path = paths.ICON_SET_DIR,
    contact_file: Path = paths.REVIEW_CONTACT_FILE,
    example_file: Path = paths.REVIEW_CONTACT_EXAMPLE,
    metadata_dir: Path = paths.METADATA_DIR,
) -> list:
    return check_icon(icon_set_dir) + check_review_contact(contact_file, example_file) + check_urls(metadata_dir)
