import json

from scripts.release.settings import load_settings, missing_settings


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_local_settings_override_committed_ones(tmp_path):
    _write(tmp_path / "settings.json", {"bundle_id": "com.example", "apple_id": "", "team_id": ""})
    _write(tmp_path / "settings.local.json", {"apple_id": "me@example.com", "team_id": "TEAM123456"})
    settings = load_settings(tmp_path / "settings.json")
    assert settings["apple_id"] == "me@example.com"
    assert settings["team_id"] == "TEAM123456"
    assert settings["bundle_id"] == "com.example"


def test_missing_local_settings_file_is_fine(tmp_path):
    _write(tmp_path / "settings.json", {"bundle_id": "com.example", "apple_id": ""})
    settings = load_settings(tmp_path / "settings.json")
    assert missing_settings(settings, ["apple_id"]) == [
        'apple_id — store/settings.local.json の "apple_id" に入力してください']
