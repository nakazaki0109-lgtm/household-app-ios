"""審査提出の直前に表示する、提出内容の要約。"""
import json
from pathlib import Path

from . import paths

from .store_rules import read_field

RELEASE_LABELS = {"manual": "手動（審査通過後、自分でリリース）", "automatic": "自動（審査通過後すぐ公開）"}


def availability_line(availability: str, territories: str) -> str:
    if availability == "applied":
        return f"無料 / {territories}（自動設定済み）"
    return f"自動設定できていません。App Store Connect の「価格および配信状況」で無料・{territories}か確認してください"


def privacy_line(privacy_file: Path) -> str:
    """App のプライバシー回答の要約。"""
    if not Path(privacy_file).exists():
        return "未設定（store/app_privacy_details.json がありません）"
    answers = json.loads(Path(privacy_file).read_text(encoding="utf-8"))
    if any("DATA_NOT_COLLECTED" in item.get("data_protections", []) for item in answers):
        return "データ収集なし"
    categories = sorted({item["category"] for item in answers if item.get("category")})
    return f"収集あり（{len(categories)}カテゴリ: {', '.join(categories)}）"


def submission_summary(version: str, build_number, settings: dict, metadata_dir: Path, screenshots_dir: Path,
                       availability: str = "manual", privacy_file: Path = paths.PRIVACY_DETAILS_FILE) -> str:
    app_store = settings["app_store"]
    description = read_field(metadata_dir, "description")
    screenshot_count = len(list(Path(screenshots_dir).rglob("*.png"))) if Path(screenshots_dir).exists() else 0
    territories = "・".join(app_store["territories"])
    lines = [
        "===== 審査提出の内容 =====",
        f"バンドルID: {settings['bundle_id']}",
        f"バージョン: {version}",
        f"ビルド番号: {build_number}",
        f"公開方法: {RELEASE_LABELS.get(app_store['release_method'], app_store['release_method'])}",
        f"価格・公開地域: {availability_line(availability, territories)}",
        f"カテゴリ: {app_store['primary_category']}",
        f"アプリ名: {read_field(metadata_dir, 'name')}",
        f"サブタイトル: {read_field(metadata_dir, 'subtitle')}",
        f"キーワード: {read_field(metadata_dir, 'keywords')}",
        f"説明文: {len(description)}文字 「{description[:40].replace(chr(10), ' ')}…」",
        f"プライバシーポリシーURL: {read_field(metadata_dir, 'privacy_url')}",
        f"サポートURL: {read_field(metadata_dir, 'support_url')}",
        f"App のプライバシー: {privacy_line(privacy_file)}",
        f"スクリーンショット: {screenshot_count}枚",
        "==========================",
    ]
    return "\n".join(lines)
