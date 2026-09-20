#!/usr/bin/env python3
"""requirements.md から、実装のチェックリストを取り出す。

機能要件 (F1, F2, ...) と受け入れ条件 (A1, A2, ...) に通し番号を振って
一覧にする。実装中・レビュー中に「どの要件を満たしたか」を番号で指せるように
するため。書式は defining-requirements の requirements_doc.py が作るものに合わせる。
ロジックは文字列を受け取る純粋関数にまとめ、pytest でテストする。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 見出し -> (ID の接頭辞, 出力上のキー)
TARGETS = {
    "機能要件": ("F", "functional"),
    "受け入れ条件": ("A", "acceptance"),
    "制約・非機能要件": ("C", "constraints"),
    "スコープ外（やらないこと）": ("X", "out_of_scope"),
    "未決事項": ("O", "open"),
}


def parse_sections(text: str) -> dict[str, list[dict[str, str]]]:
    """対象セクションの箇条書きを {キー: [{"id": "F1", "text": "..."}]} で返す。

    対象セクションが無い場合は空リストにする (requirements.md の不備は
    呼び出し側の check で見つける)。
    """
    result: dict[str, list[dict[str, str]]] = {key: [] for _, key in TARGETS.values()}
    current: tuple[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = TARGETS.get(line[3:].strip())
            continue
        if current is not None and line.startswith("- "):
            prefix, key = current
            item = line[2:].strip()
            if item:
                result[key].append({"id": f"{prefix}{len(result[key]) + 1}", "text": item})
    return result


def render_markdown(sections: dict[str, list[dict[str, str]]]) -> str:
    """実装の進捗管理に使えるチェックリストを返す。未決事項は先頭で警告する。"""
    parts: list[str] = []
    if sections["open"]:
        parts.append("## 未決事項あり (先に defining-requirements で決める)\n")
        parts.extend(f"- {i['id']}: {i['text']}\n" for i in sections["open"])
        parts.append("\n")
    labels = (
        ("functional", "機能要件"),
        ("acceptance", "受け入れ条件"),
        ("constraints", "制約・非機能要件"),
        ("out_of_scope", "スコープ外 (実装しない)"),
    )
    for key, label in labels:
        if not sections[key]:
            continue
        parts.append(f"## {label}\n")
        parts.extend(f"- [ ] {i['id']}: {i['text']}\n" for i in sections[key])
        parts.append("\n")
    return "".join(parts).rstrip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="requirements.md から実装チェックリストを作る")
    parser.add_argument("path", type=Path, help="requirements.md のパス")
    parser.add_argument("--json", action="store_true", help="JSON で出力する")
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"エラー: {args.path} がありません。先に defining-requirements で作成してください。", file=sys.stderr)
        return 1
    sections = parse_sections(args.path.read_text(encoding="utf-8"))
    if not sections["functional"]:
        print("エラー: 機能要件が1件もありません。defining-requirements に戻ってください。", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(sections, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(sections), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
