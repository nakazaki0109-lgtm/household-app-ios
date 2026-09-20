import pytest

from scripts.release.stage_state import StageState, fingerprint


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "repo"
    (root / "HouseholdApp").mkdir(parents=True)
    (root / "HouseholdAppTests").mkdir()
    (root / "store" / "metadata" / "ja").mkdir(parents=True)
    (root / "project.yml").write_text("name: x")
    (root / "HouseholdApp" / "A.swift").write_text("let a = 1")
    (root / "store" / "settings.json").write_text("{}")
    (root / "store" / "metadata" / "ja" / "name.txt").write_text("n")
    return root


@pytest.fixture
def state(project, tmp_path):
    state = StageState(tmp_path / "state" / "release_state.json", project)
    state.begin("1.0.0")
    return state


def test_stage_is_not_done_initially(state):
    assert not state.is_done("test")


def test_marked_stage_is_done_and_keeps_data(state):
    state.mark_done("build", {"build_number": "3"})
    assert state.is_done("build")
    assert state.get("build", "build_number") == "3"


def test_source_change_invalidates_stage(state, project):
    state.mark_done("test")
    (project / "HouseholdApp" / "A.swift").write_text("let a = 2")
    assert not state.is_done("test")


def test_store_change_does_not_invalidate_test_stage(state, project):
    state.mark_done("test")
    (project / "store" / "metadata" / "ja" / "name.txt").write_text("changed")
    assert state.is_done("test")


def test_rerunning_a_stage_invalidates_dependents(state):
    for stage in ["test", "build", "upload", "submit"]:
        state.mark_done(stage)
    state.mark_done("build")
    assert state.is_done("build")
    assert not state.is_done("upload")
    assert not state.is_done("submit")
    assert state.is_done("test")


def test_independent_branch_is_not_invalidated(state):
    state.mark_done("screenshots")
    state.mark_done("build")
    assert state.is_done("screenshots")


def test_new_version_discards_previous_records(state):
    state.mark_done("test")
    state.begin("1.0.1")
    assert not state.is_done("test")


def test_same_version_keeps_records(state):
    state.mark_done("test")
    state.begin("1.0.0")
    assert state.is_done("test")


def test_reset_clears_everything(state):
    state.mark_done("test")
    state.reset()
    assert not state.is_done("test")


def test_fingerprint_ignores_ds_store(project):
    before = fingerprint("test", project)
    (project / "HouseholdApp" / ".DS_Store").write_text("junk")
    assert fingerprint("test", project) == before


def test_cli_state_mark_accepts_json_with_awkward_values(state, project, tmp_path, monkeypatch):
    from functools import partial

    from scripts.release import cli

    monkeypatch.setattr(cli, "StageState", partial(StageState, tmp_path / "state" / "release_state.json", project))
    cli.main(["state", "mark", "build", '{"ipa": "/a,b=c/App.ipa", "build_number": "4"}'])
    assert state.get("build", "ipa") == "/a,b=c/App.ipa"


def test_get_returns_nothing_when_inputs_changed_after_the_stage(state, project):
    state.mark_done("build", {"build_number": "3", "ipa": "/old/App.ipa"})
    (project / "HouseholdApp" / "A.swift").write_text("let a = 2")
    assert state.get("build", "ipa") is None
    assert state.get("build", "build_number") is None
