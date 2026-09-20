#!/usr/bin/env python3
"""レビュー対象の変更ファイルを洗い出し、層ごとに分類して依存の向きの違反を検出する。

「何がレビュー対象か」の特定 (git の差分と未追跡ファイル)、Swift ファイルの層への
分類、Domain 層などが import してはいけないフレームワークの検出は、毎回同じ
結果になる決まった処理なので、モデルに任せずこのスクリプトで行う。
git の実行は run_git だけに閉じ込め、残りは文字列を受け取る純粋関数にして
pytest でテストする (tests/test_review_scope.py)。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# 層 -> その層が import してはいけないモジュール。
# 依存の向きは Views -> Services -> Domain / Models (Domain は誰にも依存しない)。
FORBIDDEN_IMPORTS: dict[str, tuple[str, ...]] = {
    "Domain": ("SwiftUI", "SwiftData", "UIKit"),
    "Models": ("SwiftUI", "UIKit"),
    "Services": ("SwiftUI", "UIKit"),
}
LAYERS = ("Domain", "Models", "Services", "Views")

# 行頭の `import Foo` / `@testable import Foo` / `import struct Foo.Bar` から、最上位のモジュール名を取る。
# 空白は改行を跨がないよう [ \t] に限る (跨ぐと次の行の単語を拾ってしまう)。
IMPORT_RE = re.compile(
    r"^[ \t]*(?:@\w+[ \t]+)*import[ \t]+(?:(?:struct|class|enum|protocol|typealias|func|var|let)[ \t]+)?([A-Za-z_]\w*)",
    re.MULTILINE,
)
STATUS_LABELS = {"A": "追加", "M": "変更", "D": "削除", "R": "改名", "C": "複製", "U": "未追跡"}


@dataclass(frozen=True)
class Change:
    path: str
    status: str  # A / M / D / R / U (未追跡)

    @property
    def is_swift(self) -> bool:
        return self.path.endswith(".swift")

    @property
    def is_test(self) -> bool:
        return self.is_swift and any(p.endswith("Tests") for p in Path(self.path).parts[:-1])

    @property
    def layer(self) -> str | None:
        """Swift のアプリコードなら所属する層を、それ以外は None を返す。"""
        if not self.is_swift or self.is_test:
            return None
        parts = Path(self.path).parts[:-1]
        for layer in LAYERS:
            if layer in parts:
                return layer
        return None


@dataclass(frozen=True)
class Violation:
    path: str
    layer: str
    module: str


def parse_name_status(text: str) -> list[Change]:
    """`git diff --name-status` の出力を Change の一覧にする。改名は新しい側のパスを採る。"""
    changes: list[Change] = []
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) < 2 or not fields[0]:
            continue
        changes.append(Change(path=fields[-1], status=fields[0][0]))
    return changes


def parse_untracked(text: str) -> list[Change]:
    return [Change(path=line.strip(), status="U") for line in text.splitlines() if line.strip()]


def merge_changes(*groups: list[Change]) -> list[Change]:
    """同じパスは後のグループを優先して1件にまとめ、パス順に並べる。"""
    merged: dict[str, Change] = {}
    for group in groups:
        for change in group:
            merged[change.path] = change
    return sorted(merged.values(), key=lambda c: c.path)


def find_import_violations(change: Change, content: str) -> list[Violation]:
    """変更ファイルが、その層に許されないモジュールを import していれば返す。"""
    layer = change.layer
    if layer is None or layer not in FORBIDDEN_IMPORTS:
        return []
    imported = set(IMPORT_RE.findall(content))
    return [
        Violation(change.path, layer, module)
        for module in FORBIDDEN_IMPORTS[layer]
        if module in imported
    ]


def render_report(
    changes: list[Change], violations: list[Violation], has_requirements: bool, target: str
) -> str:
    if not changes:
        return f"レビュー対象: {target}\n変更はありません。\n"
    swift_app = [c for c in changes if c.layer is not None]
    lines = [f"レビュー対象: {target}", f"変更ファイル: {len(changes)} 件 (うち Swift のアプリコード {len(swift_app)} 件)\n"]
    for c in changes:
        layer = c.layer or ("Test" if c.is_test else "-")
        lines.append(f"- [{STATUS_LABELS.get(c.status, c.status)}] {c.path} ({layer})")
    lines.append("")
    if violations:
        lines.append("依存の向きの違反 (機械検出):")
        lines.extend(f"- {v.path}: {v.layer} 層が {v.module} を import している" for v in violations)
    else:
        lines.append("依存の向きの違反 (機械検出): なし")
    lines.append(f"requirements.md: {'あり' if has_requirements else 'なし'}")
    return "\n".join(lines) + "\n"


def run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} に失敗しました: {proc.stderr.strip()}")
    return proc.stdout


def collect_changes(base: str | None) -> tuple[list[Change], str]:
    """対象の変更一覧と、その説明を返す。

    base 無し: 作業ツリーとインデックスの HEAD からの変更 + 未追跡ファイル。
    base 有り: base とのマージ基点から HEAD までのブランチの変更 (コミット済みのみ)。
    """
    if base:
        diff = parse_name_status(run_git(["diff", "--name-status", f"{base}...HEAD"]))
        return merge_changes(diff), f"{base} からのブランチの変更"
    diff = parse_name_status(run_git(["diff", "--name-status", "HEAD"]))
    untracked = parse_untracked(run_git(["ls-files", "--others", "--exclude-standard"]))
    return merge_changes(diff, untracked), "作業ツリーの変更 (未コミット + 未追跡)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="レビュー対象の変更を洗い出す")
    parser.add_argument("--base", help="比較元のブランチ/コミット (例: main)。省略時は作業ツリーの変更")
    parser.add_argument("--requirements", default="requirements.md", type=Path)
    args = parser.parse_args(argv)

    try:
        changes, target = collect_changes(args.base)
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 2

    violations: list[Violation] = []
    for change in changes:
        path = Path(change.path)
        if change.status != "D" and path.is_file():
            violations.extend(find_import_violations(change, path.read_text(encoding="utf-8", errors="replace")))

    print(render_report(changes, violations, args.requirements.exists(), target), end="")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
