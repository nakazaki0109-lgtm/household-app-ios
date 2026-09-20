#!/usr/bin/env python3
"""2つのファイルからunified diffを生成する。

このスキルは対象文書を直接書き換えず、必ず「提案」として差分を見せてから
ユーザーの承認を待つ。差分表示という決定的な処理をモデルに毎回組み立てさせず
difflibに任せる。ロジックはrender_diff()に集約し、pytestでテストする
(tests/test_render_diff.py)。
"""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def render_diff(
    original_path: Path,
    proposed_path: Path,
    *,
    context_lines: int = 3,
) -> str:
    """original_pathの現状の内容と、proposed_pathに書かれた提案内容を比較し、
    unified diff形式の文字列を返す。どちらのファイルも変更しない。
    """
    original_lines = Path(original_path).read_text(encoding="utf-8").splitlines(keepends=True)
    proposed_lines = Path(proposed_path).read_text(encoding="utf-8").splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        proposed_lines,
        fromfile=f"a/{Path(original_path).name} (現状)",
        tofile=f"b/{Path(original_path).name} (提案)",
        n=context_lines,
    )
    return "".join(diff)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="現状のファイルと提案ファイルのunified diffを表示する(どちらも書き換えない)"
    )
    parser.add_argument("original", type=Path, help="現状のファイルパス")
    parser.add_argument("proposed", type=Path, help="提案内容を書いたファイルパス")
    parser.add_argument("--context", type=int, default=3, help="前後に表示する文脈行数")
    args = parser.parse_args(argv)

    diff_text = render_diff(args.original, args.proposed, context_lines=args.context)
    print(diff_text if diff_text else "差分なし")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
