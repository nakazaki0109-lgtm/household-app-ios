import json

from scripts.release import deliver_stage
from scripts.release.name_candidates import candidate, load_candidates, retry_guidance, apply_name
from scripts.release.session import session_guidance
from scripts.release.summary import submission_summary
import os
import pytest

SETTINGS = {
    "bundle_id": "com.example.app",
    "copyright": "2026 Someone",
    "app_store": {
        "primary_category": "FINANCE", "price_tier": 0, "territories": ["JPN"], "release_method": "manual",
        "uses_non_exempt_encryption": False, "demo_account_required": False, "review_notes": "",
        "age_rating": {"gambling": False},
    },
}


@pytest.fixture
def files(tmp_path):
    metadata = tmp_path / "metadata"
    metadata.mkdir()
    (metadata / "name.txt").write_text("名前\n")
    (metadata / "subtitle.txt").write_text("副題\n")
    (metadata / "privacy_url.txt").write_text("")
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps(SETTINGS))
    return tmp_path, metadata, settings


def test_empty_fields_are_not_staged(files):
    tmp_path, metadata, settings = files
    options = deliver_stage.stage_deliver(tmp_path / "out", settings, metadata, tmp_path / "none.json")
    assert options["fields"] == ["name", "subtitle"]
    assert not (tmp_path / "out" / "metadata" / "ja" / "privacy_url.txt").exists()


def test_review_information_only_when_contact_complete(files):
    tmp_path, metadata, settings = files
    contact = tmp_path / "contact.json"
    contact.write_text(json.dumps({"first_name": "a", "last_name": "b", "phone_number": "090", "email_address": "e@x.y"}))
    options = deliver_stage.stage_deliver(tmp_path / "out", settings, metadata, contact)
    info = json.loads(open(options["review_information_path"]).read())
    assert info["phone_number"] == "090"
    assert info["demo_account_required"] is False

    contact.write_text(json.dumps({"first_name": "a"}))
    options = deliver_stage.stage_deliver(tmp_path / "out", settings, metadata, contact)
    assert options["review_information_path"] is None
    assert not (tmp_path / "out" / "review_information.json").exists()


def test_summary_shows_version_build_release_method(files):
    tmp_path, metadata, _ = files
    text = submission_summary("1.0.0", 7, SETTINGS | {}, metadata, tmp_path / "shots")
    assert "バージョン: 1.0.0" in text
    assert "ビルド番号: 7" in text
    assert "手動" in text
    assert "アプリ名: 名前" in text


def test_name_candidates_skip_comments_and_validate(tmp_path):
    path = tmp_path / "names.txt"
    path.write_text("# comment\n\nA名\n" + "あ" * 31 + "\nC名\n")
    assert load_candidates(path) == ["A名", "あ" * 31, "C名"]
    assert candidate(1, path) == "A名"
    with pytest.raises(ValueError, match="31文字"):
        candidate(2, path)
    with pytest.raises(ValueError, match="候補4はありません"):
        candidate(4, path)


def test_retry_guidance_points_to_next_candidate_or_says_exhausted(tmp_path):
    path = tmp_path / "names.txt"
    path.write_text("A\nB\n")
    assert "candidate:2" in retry_guidance(1, path)
    assert "重複が原因なら" in retry_guidance(1, path)
    assert "残っていません" in retry_guidance(2, path)


def test_apply_name_writes_name_file(tmp_path):
    apply_name("新名前", tmp_path)
    assert (tmp_path / "name.txt").read_text(encoding="utf-8") == "新名前\n"


def test_session_guidance_missing_fresh_and_stale(tmp_path):
    assert "ありません" in session_guidance("me@example.com", tmp_path)
    cookie = tmp_path / ".fastlane" / "spaceship" / "me@example.com" / "cookie"
    cookie.parent.mkdir(parents=True)
    cookie.write_text("x")
    assert session_guidance("me@example.com", tmp_path) is None
    old = cookie.stat().st_mtime - 40 * 86400
    os.utime(cookie, (old, old))
    assert "期限切れ" in session_guidance("me@example.com", tmp_path)


def test_summary_reports_availability_state(files):
    tmp_path, metadata, _ = files
    applied = submission_summary("1.0.0", 7, SETTINGS, metadata, tmp_path / "shots", "applied")
    assert "自動設定済み" in applied
    manual = submission_summary("1.0.0", 7, SETTINGS, metadata, tmp_path / "shots")
    assert "自動設定できていません" in manual


def test_privacy_line_for_no_collection_collection_and_missing(tmp_path):
    from scripts.release.summary import privacy_line

    none_file = tmp_path / "none.json"
    none_file.write_text('[{"data_protections": ["DATA_NOT_COLLECTED"]}]')
    assert privacy_line(none_file) == "データ収集なし"

    some_file = tmp_path / "some.json"
    some_file.write_text('[{"category": "USAGE_DATA", "purposes": ["ANALYTICS"], "data_protections": ["DATA_NOT_LINKED_TO_YOU"]}]')
    assert "1カテゴリ: USAGE_DATA" in privacy_line(some_file)

    assert "未設定" in privacy_line(tmp_path / "missing.json")
