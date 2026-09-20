"""xcodebuild test の出力から失敗したテスト名を取り出し、テストを実行する。"""
import re
import subprocess
from pathlib import Path

from . import paths

FAILED_TEST = re.compile(r"Test [Cc]ase '(?P<name>[^']+)' failed")
BUILD_ERROR = re.compile(r"^.*: error: .*$", re.MULTILINE)


def failed_tests(output: str) -> list:
    """失敗したテスト名を、出現順・重複なしで返す。"""
    names = []
    for match in FAILED_TEST.finditer(output):
        name = match.group("name")
        if name not in names:
            names.append(name)
    return names


def build_errors(output: str) -> list:
    return list(dict.fromkeys(m.group(0).strip() for m in BUILD_ERROR.finditer(output)))[:10]


def xcodebuild_test_command(destination: str) -> list:
    return [
        "xcodebuild", "-project", "HouseholdApp.xcodeproj", "-scheme", "HouseholdApp",
        "-destination", destination, "test",
    ]


def run_tests(destination: str, log_file: Path = None) -> int:
    """テストを実行して結果を表示する。0 で成功、1 でテスト失敗、2 でビルド失敗。"""
    log_file = Path(log_file or paths.LOG_DIR / "test.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    print("ユニットテストを実行中...", flush=True)
    result = subprocess.run(
        xcodebuild_test_command(destination), cwd=paths.ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
    )
    log_file.write_text(result.stdout, encoding="utf-8")
    if result.returncode == 0:
        print("テスト成功")
        return 0

    names = failed_tests(result.stdout)
    if names:
        print(f"テスト失敗 ({len(names)}件):")
        for name in names:
            print(f"  ✗ {name}")
        print(f"詳細ログ: {log_file}")
        return 1

    print("テストを実行できませんでした (ビルドまたは実行環境のエラー):")
    for line in build_errors(result.stdout) or ["(error 行なし。ログを確認してください)"]:
        print(f"  {line}")
    print(f"詳細ログ: {log_file}")
    return 2
