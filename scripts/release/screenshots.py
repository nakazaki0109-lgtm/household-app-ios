"""シミュレータでスクリーンショットを自動撮影する。"""
import json
import re
import subprocess
import time
from pathlib import Path

from . import paths
from .settings import load_settings

BUNDLE_ID_KEY = "bundle_id"
WARMUP_SECONDS = 8


def pick_simulator(devices_json: dict, name: str):
    """名前が一致する利用可能なシミュレータのうち、最新の iOS のものを (udid, runtime) で返す。"""
    candidates = []
    for runtime, devices in devices_json.get("devices", {}).items():
        match = re.search(r"iOS-(\d+)-(\d+)", runtime)
        if not match:
            continue
        version = (int(match.group(1)), int(match.group(2)))
        for device in devices:
            if device.get("name") == name and device.get("isAvailable", True):
                candidates.append((version, device["udid"], runtime))
    if not candidates:
        return None
    _, udid, runtime = max(candidates)
    return udid, runtime


def launch_arguments(tab: int) -> list:
    return ["-ScreenshotSampleData", "-ScreenshotTab", str(tab), "-AppleLanguages", "(ja)", "-AppleLocale", "ja_JP"]


def screenshot_filename(device: str, index: int, scene: str) -> str:
    return f"{device}_{index:02d}_{scene}.png"


def _run(command: list, **kwargs):
    return subprocess.run(command, check=True, cwd=paths.ROOT, **kwargs)


def _simctl(*args: str, **kwargs):
    return _run(["xcrun", "simctl", *args], **kwargs)


def capture(settings_file: Path = paths.SETTINGS_FILE, out_dir: Path = paths.SCREENSHOTS_DIR) -> int:
    settings = load_settings(settings_file)
    bundle_id = settings[BUNDLE_ID_KEY]
    listing = subprocess.run(["xcrun", "simctl", "list", "devices", "available", "-j"],
                             check=True, capture_output=True, text=True)
    devices_json = json.loads(listing.stdout)

    targets = []
    for device in settings["screenshots"]["devices"]:
        found = pick_simulator(devices_json, device["simulator"])
        if found is None:
            print(f"シミュレータ「{device['simulator']}」が見つかりません (xcrun simctl list devices)")
            return 1
        targets.append((device, found[0]))

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()

    derived = paths.BUILD_DIR / "screenshots-derived"
    for device, udid in targets:
        print(f"[{device['name']}] {device['simulator']} を準備中...", flush=True)
        _simctl("bootstatus", udid, "-b", stdout=subprocess.DEVNULL)
        try:
            _simctl("status_bar", udid, "override", "--time", "9:41", "--batteryState", "charged",
                    "--batteryLevel", "100", "--cellularBars", "4", "--wifiBars", "3")
            _simctl("ui", udid, "appearance", "light")
            _run(["xcodebuild", "-project", "HouseholdApp.xcodeproj", "-scheme", "HouseholdApp",
                  "-destination", f"id={udid}", "-derivedDataPath", str(derived), "-quiet", "build"])
            app_path = derived / "Build" / "Products" / "Debug-iphonesimulator" / "HouseholdApp.app"
            _simctl("install", udid, str(app_path))
            # 起動直後は画面が整わないことがあるため、一度起動して待ってから撮り始める
            _simctl("launch", "--terminate-running-process", udid, bundle_id, *launch_arguments(0),
                    stdout=subprocess.DEVNULL)
            time.sleep(WARMUP_SECONDS)
            for index, scene in enumerate(settings["screenshots"]["scenes"], start=1):
                _simctl("launch", "--terminate-running-process", udid, bundle_id, *launch_arguments(scene["tab"]),
                        stdout=subprocess.DEVNULL)
                time.sleep(3)
                target = out_dir / screenshot_filename(device["name"], index, scene["name"])
                _simctl("io", udid, "screenshot", "--type=png", str(target))
                print(f"  撮影: {target.relative_to(paths.ROOT)}")
        finally:
            _simctl("shutdown", udid)
    return 0
