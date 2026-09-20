#!/usr/bin/env python3
"""xcodebuild のビルドログから、型チェックが遅い関数・式を抜き出して報告する。

Swift コンパイラの -warn-long-function-bodies / -warn-long-expression-type-checking
が出す警告をパースし、遅い順に並べる。コンパイル時間の劣化を「感覚」ではなく
数字で見つけるための計測用。ロジック (コマンド組み立て・ログのパース・整形) は
純粋関数にし、pytest でテストする。xcodebuild を実際に走らせるのは run サブコマンド
だけで、薄いラッパーにとどめている。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# 例: /path/Foo.swift:12:8: warning: instance method 'bar()' took 312ms to type-check (limit: 200ms)
#     /path/Foo.swift:30:5: warning: expression took 150ms to type-check (limit: 100ms)
WARNING_RE = re.compile(
    r"^(?P<file>.+?\.swift):(?P<line>\d+):\d+: warning: "
    r"(?P<what>.+?) took (?P<ms>\d+)ms to type-check \(limit: (?P<limit>\d+)ms\)"
)


@dataclass(frozen=True)
class SlowSpot:
    file: str
    line: int
    what: str
    ms: int

    @property
    def is_expression(self) -> bool:
        return self.what.startswith("expression")


def build_command(
    project: str, scheme: str, destination: str, function_ms: int, expression_ms: int
) -> list[str]:
    """遅い箇所の警告を有効にした、クリーンビルドの xcodebuild コマンドを返す。

    クリーンビルドにするのは、増分ビルドだと変更のない関数が再コンパイルされず、
    計測から漏れるため。
    """
    flags = (
        f"-Xfrontend -warn-long-function-bodies={function_ms} "
        f"-Xfrontend -warn-long-expression-type-checking={expression_ms}"
    )
    return [
        "xcodebuild",
        "-project", project,
        "-scheme", scheme,
        "-destination", destination,
        f"OTHER_SWIFT_FLAGS={flags}",
        "clean", "build",
    ]


def parse_log(text: str) -> list[SlowSpot]:
    """ログから遅い箇所を取り出し、遅い順・同一箇所は最大値で1件にして返す。"""
    worst: dict[tuple[str, int, str], SlowSpot] = {}
    for line in text.splitlines():
        m = WARNING_RE.match(line.strip())
        if not m:
            continue
        spot = SlowSpot(m["file"], int(m["line"]), m["what"], int(m["ms"]))
        key = (spot.file, spot.line, spot.what)
        if key not in worst or worst[key].ms < spot.ms:
            worst[key] = spot
    return sorted(worst.values(), key=lambda s: s.ms, reverse=True)


def render_report(spots: list[SlowSpot], top: int) -> str:
    if not spots:
        return "型チェックが遅い箇所はありません。\n"
    lines = [f"型チェックが遅い箇所: {len(spots)} 件 (上位 {min(top, len(spots))} 件を表示)\n"]
    for s in spots[:top]:
        kind = "式" if s.is_expression else "関数"
        lines.append(f"- {s.ms}ms [{kind}] {s.file}:{s.line} {s.what}\n")
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Swift の型チェックが遅い箇所を計測する")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="xcodebuild を実行して計測する")
    run.add_argument("--project", default="HouseholdApp.xcodeproj")
    run.add_argument("--scheme", default="HouseholdApp")
    run.add_argument("--destination", default="generic/platform=iOS Simulator")
    run.add_argument("--function-ms", type=int, default=200, help="関数本体の警告しきい値")
    run.add_argument("--expression-ms", type=int, default=100, help="式の警告しきい値")
    run.add_argument("--top", type=int, default=10)

    parse = sub.add_parser("parse", help="保存済みのビルドログを解析する")
    parse.add_argument("log", type=Path)
    parse.add_argument("--top", type=int, default=10)

    args = parser.parse_args(argv)

    if args.cmd == "run":
        cmd = build_command(args.project, args.scheme, args.destination, args.function_ms, args.expression_ms)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout[-4000:], file=sys.stderr)
            print("エラー: ビルドに失敗したため計測できません。", file=sys.stderr)
            return 2
        text = proc.stdout
    else:
        text = args.log.read_text(encoding="utf-8", errors="replace")

    spots = parse_log(text)
    print(render_report(spots, args.top), end="")
    return 1 if spots else 0


if __name__ == "__main__":
    sys.exit(main())
