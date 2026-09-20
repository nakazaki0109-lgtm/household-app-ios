"""シナリオの前提に合わせて、iPhone シミュレータでアプリを起動する。

画面操作と確認は mobile-mcp が行う。mobile-mcp の起動ツールは起動引数を渡せないので、
前提データの指定を含む起動だけをここで xcrun simctl で行う。
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from scripts.release import paths
from scripts.release.screenshots import pick_simulator

SIMULATOR_NAME = "iPhone 16"
BUNDLE_ID = "com.nakazaki.householdapp"
MOBILE_MCP_PACKAGE = "@mobilenext/mobile-mcp@1.0.4"  # .mcp.json と同じバージョンに揃える
SCENARIOS_DIR = paths.ROOT / "scenarios"
RESULTS_DIR = paths.BUILD_DIR / "scenario-results"
DERIVED_DIR = paths.BUILD_DIR / "scenario-derived"

SAMPLE_DATA = "サンプルデータあり"
EMPTY_STATE = "空の初期状態"
PRECONDITIONS = (SAMPLE_DATA, EMPTY_STATE)

_PRECONDITION_LINE = re.compile(r"^前提[:：]\s*(.+?)\s*$", re.MULTILINE)


class ScenarioError(Exception):
    """シナリオの書き方が誤っているときの、利用者向けメッセージ付きの例外。"""


def parse_precondition(text: str) -> str:
    match = _PRECONDITION_LINE.search(text)
    if match is None:
        raise ScenarioError(f"「前提: {SAMPLE_DATA}」または「前提: {EMPTY_STATE}」の行がありません")
    value = match.group(1)
    if value not in PRECONDITIONS:
        raise ScenarioError(f"前提「{value}」は使えません。{' / '.join(PRECONDITIONS)} のどちらかにしてください")
    return value


def launch_arguments(precondition: str) -> list:
    """サンプルデータは -ScreenshotSampleData (インメモリ)。空の初期状態は起動引数なし (再インストール済みの新規ストア)。"""
    arguments = ["-AppleLanguages", "(ja)", "-AppleLocale", "ja_JP"]
    if precondition == SAMPLE_DATA:
        arguments = ["-ScreenshotSampleData", *arguments]
    return arguments


def results_dir_for(scenario_file: Path) -> Path:
    return RESULTS_DIR / Path(scenario_file).stem


def _run(command: list, check: bool = True, **kwargs):
    return subprocess.run(command, check=check, cwd=paths.ROOT, **kwargs)


def _simctl(*args: str, check: bool = True, **kwargs):
    return _run(["xcrun", "simctl", *args], check=check, **kwargs)


def _find_udid() -> str:
    listing = subprocess.run(["xcrun", "simctl", "list", "devices", "available", "-j"],
                             check=True, capture_output=True, text=True)
    found = pick_simulator(json.loads(listing.stdout), SIMULATOR_NAME)
    if found is None:
        raise ScenarioError(f"シミュレータ「{SIMULATOR_NAME}」が見つかりません (xcrun simctl list devices)")
    return found[0]


def _ensure_mobile_mcp_agent(udid: str) -> None:
    """mobile-mcp が画面を操作するための常駐エージェントを、シミュレータに入れる (入れ済みなら何もしない)。

    初回はエージェントの起動でホーム画面に戻るので、アプリの起動より前に済ませておく。
    """
    _run(["npx", "-y", "-p", MOBILE_MCP_PACKAGE, "mobilecli", "agent", "install", "--device", udid],
         stdout=subprocess.DEVNULL)


def launch(scenario_file: Path, build: bool = True) -> tuple:
    """アプリを前提の状態で起動し、(シミュレータの UDID, 結果の保存先) を返す。"""
    scenario_file = Path(scenario_file)
    if not scenario_file.is_file():
        raise ScenarioError(f"シナリオが見つかりません: {scenario_file}")
    precondition = parse_precondition(scenario_file.read_text(encoding="utf-8"))
    udid = _find_udid()

    _simctl("boot", udid, check=False, stderr=subprocess.DEVNULL)  # 起動済みなら失敗するが問題ない
    _simctl("bootstatus", udid, "-b", stdout=subprocess.DEVNULL)

    if build:
        _run(["xcodebuild", "-project", "HouseholdApp.xcodeproj", "-scheme", "HouseholdApp",
              "-destination", f"id={udid}", "-derivedDataPath", str(DERIVED_DIR), "-quiet", "build"])
    app_path = DERIVED_DIR / "Build" / "Products" / "Debug-iphonesimulator" / "HouseholdApp.app"
    if not app_path.is_dir():
        raise ScenarioError(f"ビルド済みのアプリがありません: {app_path}")

    _ensure_mobile_mcp_agent(udid)

    _simctl("terminate", udid, BUNDLE_ID, check=False, stderr=subprocess.DEVNULL)
    if precondition == EMPTY_STATE:
        # アンインストールで端末内のデータを消し、取引0件・既定6カテゴリの状態から始める
        _simctl("uninstall", udid, BUNDLE_ID, check=False, stderr=subprocess.DEVNULL)
    _simctl("install", udid, str(app_path))
    _simctl("launch", udid, BUNDLE_ID, *launch_arguments(precondition), stdout=subprocess.DEVNULL)

    results = results_dir_for(scenario_file)
    shutil.rmtree(results, ignore_errors=True)
    results.mkdir(parents=True)
    return udid, results
