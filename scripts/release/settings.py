"""store/settings.json の読み込み。個人情報は Git 管理外の settings.local.json で上書きする。"""
import json
from pathlib import Path

from . import paths


def load_settings(path: Path = paths.SETTINGS_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    local = path.with_name(paths.LOCAL_SETTINGS_NAME)
    if local.exists():
        with open(local, encoding="utf-8") as f:
            settings.update(json.load(f))
    return settings


def missing_settings(settings: dict, required: list) -> list:
    """未入力の設定キーを `store/settings.local.json` の場所つきで返す。"""
    lines = []
    for key in required:
        if not str(settings.get(key, "")).strip():
            lines.append(f"{key} — store/settings.local.json の \"{key}\" に入力してください")
    return lines
