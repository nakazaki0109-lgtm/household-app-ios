import pytest

from scripts.release.stage_state import StageState
from scripts.release.status import INTERACTIVE_STAGES, release_status


@pytest.fixture
def state(tmp_path):
    root = tmp_path / "repo"
    (root / "HouseholdApp").mkdir(parents=True)
    (root / "HouseholdAppTests").mkdir()
    (root / "store" / "metadata").mkdir(parents=True)
    (root / "project.yml").write_text("name: x")
    (root / "store" / "settings.json").write_text("{}")
    state = StageState(tmp_path / "state.json", root)
    state.begin("1.0.0")
    return state


SETTINGS = {"apple_id": "a@example.com", "team_id": "TEAM"}


def test_fresh_state_starts_at_test(state, tmp_path):
    result = release_status("1.0.0", state, SETTINGS, home=tmp_path)
    assert result["done"] == []
    assert result["next_stage"] == "test"


def test_next_stage_follows_last_done_stage(state, tmp_path):
    state.mark_done("test")
    result = release_status("1.0.0", state, SETTINGS, home=tmp_path)
    assert result["done"] == ["test"]
    assert result["next_stage"] == "build"


def test_different_version_ignores_recorded_stages(state, tmp_path):
    state.mark_done("test")
    result = release_status("1.1.0", state, SETTINGS, home=tmp_path)
    assert result["done"] == []
    assert result["next_stage"] == "test"


def test_all_done_has_no_next_stage(state, tmp_path):
    for stage in ["test", "build", "upload", "screenshots", "metadata", "submit"]:
        state.mark_done(stage)
    assert release_status("1.0.0", state, SETTINGS, home=tmp_path)["next_stage"] is None


def test_missing_settings_are_reported(state, tmp_path):
    result = release_status("1.0.0", state, {"apple_id": "", "team_id": ""}, home=tmp_path)
    assert len(result["missing_settings"]) == 2
    assert result["login_guidance"] is None


def test_login_guidance_when_no_session_cookie(state, tmp_path):
    assert release_status("1.0.0", state, SETTINGS, home=tmp_path)["login_guidance"]


def test_no_login_guidance_when_session_cookie_is_fresh(state, tmp_path):
    cookie = tmp_path / ".fastlane" / "spaceship" / "a@example.com" / "cookie"
    cookie.parent.mkdir(parents=True)
    cookie.write_text("x")
    assert release_status("1.0.0", state, SETTINGS, home=tmp_path)["login_guidance"] is None


def test_submit_is_always_interactive():
    assert "submit" in INTERACTIVE_STAGES
