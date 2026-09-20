"""store/settings.json の読み込み。"""
import json
from pathlib import Path

from . import paths


def load_settings(path: Path = paths.SETTINGS_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def missing_settings(settings: dict, required: list) -> list:
    """未入力の設定キーを `store/settings.json` の場所つきで返す。"""
    lines = []
    for key in required:
        if not str(settings.get(key, "")).strip():
            lines.append(f"{key} — store/settings.json の \"{key}\" に入力してください")
    return lines
