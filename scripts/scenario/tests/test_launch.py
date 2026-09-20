import json

import pytest

from scripts.release import paths
from scripts.scenario.launch import (
    EMPTY_STATE,
    SAMPLE_DATA,
    MOBILE_MCP_PACKAGE,
    ScenarioError,
    launch,
    launch_arguments,
    parse_precondition,
    results_dir_for,
)


def test_precondition_is_read_from_the_header_line():
    assert parse_precondition("# 題名\n\n前提: サンプルデータあり\n\n## 手順\n") == SAMPLE_DATA
    assert parse_precondition("前提：空の初期状態") == EMPTY_STATE


def test_missing_precondition_is_an_error():
    with pytest.raises(ScenarioError, match="前提"):
        parse_precondition("# 題名\n\n## 手順\n1. 何かする\n")


def test_unknown_precondition_is_an_error_and_lists_choices():
    with pytest.raises(ScenarioError, match="サンプルデータあり"):
        parse_precondition("前提: データ少なめ\n")


def test_sample_data_passes_the_screenshot_flag_and_empty_state_does_not():
    assert launch_arguments(SAMPLE_DATA)[0] == "-ScreenshotSampleData"
    assert "-ScreenshotSampleData" not in launch_arguments(EMPTY_STATE)


def test_results_are_kept_under_build_which_git_ignores():
    assert results_dir_for("scenarios/transaction-create.md").parts[-3:] == (
        "build", "scenario-results", "transaction-create")


def test_launch_rejects_a_missing_scenario_file(tmp_path):
    with pytest.raises(ScenarioError, match="見つかりません"):
        launch(tmp_path / "nothing.md")


def test_mcp_json_pins_the_same_mobile_mcp_version_the_launcher_installs_the_agent_from():
    config = json.loads((paths.ROOT / ".mcp.json").read_text(encoding="utf-8"))
    assert MOBILE_MCP_PACKAGE in config["mcpServers"]["mobile-mcp"]["args"]
