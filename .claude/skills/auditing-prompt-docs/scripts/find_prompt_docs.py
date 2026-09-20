#!/usr/bin/env python3
"""プロンプトが書かれた文書 (SKILL.md, CLAUDE.md, AGENTS.md) をリポジトリから
機械的に探す。

対象文書を見つける作業はモデルに何度もGlob/Bashを打たせず、このスクリプトに
任せる。除外ディレクトリや対象ファイル名の判断はここに集約し、pytestで
テストする (tests/test_find_prompt_docs.py)。
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

DEFAULT_TARGET_NAMES = ("SKILL.md", "CLAUDE.md", "AGENTS.md")

DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        ".build",
        "build",
        "DerivedData",
        "Pods",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }
)


def find_prompt_docs(
    root: Path,
    *,
    target_names: tuple[str, ...] = DEFAULT_TARGET_NAMES,
    excluded_dirs: frozenset[str] = DEFAULT_EXCLUDED_DIRS,
) -> list[Path]:
    """root配下から対象ファイル名に一致するファイルを再帰的に探し、パスの
    ソート済みリストを返す。excluded_dirsに含まれる名前のディレクトリには
    降りない。
    """
    root = Path(root)
    matches: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        for filename in filenames:
            if filename in target_names:
                matches.append(Path(dirpath) / filename)
    return sorted(matches)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="プロンプト文書 (SKILL.md/CLAUDE.md/AGENTS.md) をリポジトリから探す"
    )
    parser.add_argument("root", type=Path, help="探索する起点ディレクトリ")
    parser.add_argument(
        "--name",
        action="append",
        dest="names",
        help="対象ファイル名を追加指定する(複数指定可、省略時はSKILL.md/CLAUDE.md/AGENTS.md)",
    )
    args = parser.parse_args(argv)

    target_names = tuple(args.names) if args.names else DEFAULT_TARGET_NAMES
    for path in find_prompt_docs(args.root, target_names=target_names):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
