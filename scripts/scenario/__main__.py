"""使い方: python3 -m scripts.scenario launch scenarios/<シナリオ>.md [--no-build]"""
import argparse
import sys
from pathlib import Path

from .launch import ScenarioError, launch


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m scripts.scenario")
    sub = parser.add_subparsers(dest="command", required=True)
    launch_parser = sub.add_parser("launch", help="シナリオの前提の状態でアプリを起動する")
    launch_parser.add_argument("scenario", type=Path)
    launch_parser.add_argument("--no-build", action="store_true", help="ビルドを飛ばして前回のビルド結果を使う")
    args = parser.parse_args(argv)

    try:
        udid, results = launch(args.scenario, build=not args.no_build)
    except ScenarioError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    print(f"udid: {udid}")
    print(f"results: {results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
