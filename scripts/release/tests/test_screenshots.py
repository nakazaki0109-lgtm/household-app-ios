from scripts.release.screenshots import launch_arguments, pick_simulator, screenshot_filename

DEVICES = {
    "devices": {
        "com.apple.CoreSimulator.SimRuntime.iOS-17-5": [
            {"name": "iPad Pro 13-inch (M4)", "udid": "OLD", "isAvailable": True},
        ],
        "com.apple.CoreSimulator.SimRuntime.iOS-18-3": [
            {"name": "iPad Pro 13-inch (M4)", "udid": "NEW", "isAvailable": True},
            {"name": "iPhone 16 Pro Max", "udid": "PHONE", "isAvailable": True},
            {"name": "iPhone 16", "udid": "BROKEN", "isAvailable": False},
        ],
        "com.apple.CoreSimulator.SimRuntime.watchOS-11-2": [
            {"name": "iPhone 16 Pro Max", "udid": "WATCH", "isAvailable": True},
        ],
    }
}


def test_newest_ios_runtime_wins():
    assert pick_simulator(DEVICES, "iPad Pro 13-inch (M4)")[0] == "NEW"


def test_non_ios_runtime_is_ignored():
    assert pick_simulator(DEVICES, "iPhone 16 Pro Max")[0] == "PHONE"


def test_unavailable_or_unknown_device_returns_none():
    assert pick_simulator(DEVICES, "iPhone 16") is None
    assert pick_simulator(DEVICES, "iPhone 99") is None


def test_launch_arguments_select_tab_and_sample_data():
    args = launch_arguments(2)
    assert args[:3] == ["-ScreenshotSampleData", "-ScreenshotTab", "2"]


def test_screenshot_filename_is_sortable():
    assert screenshot_filename("iphone69", 1, "summary") == "iphone69_01_summary.png"
