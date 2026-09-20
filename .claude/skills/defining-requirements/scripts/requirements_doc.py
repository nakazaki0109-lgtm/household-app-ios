#!/usr/bin/env python3
"""requirements.md の作成・追記・完成度チェックを行う。

決まった書式でのファイル操作 (雛形作成、セクションへの箇条書き追記、
未決事項の解消、実装に入れる状態かの判定) はモデルに毎回考えさせず、
このスクリプトに任せる。ロジックは文字列を受け取って文字列を返す純粋関数に
まとめ、pytest でテストする (tests/test_requirements_doc.py)。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# キー -> 見出し。ファイル上の並び順もこの順。
SECTIONS = {
    "purpose": "目的と対象ユーザー",
    "in-scope": "スコープ（やること）",
    "out-of-scope": "スコープ外（やらないこと）",
    "functional": "機能要件",
    "acceptance": "受け入れ条件",
    "constraints": "制約・非機能要件",
    "open": "未決事項",
}

# 実装に入る前に最低限埋まっていてほしいセクション
REQUIRED_FILLED = ("purpose", "functional", "acceptance", "out-of-scope")


def render_template(title: str) -> str:
    """空の requirements.md の本文を返す。"""
    parts = [f"# {title} 要件定義\n"]
    for heading in SECTIONS.values():
        parts.append(f"\n## {heading}\n")
    return "".join(parts)


def _heading_line(key: str) -> str:
    return f"## {SECTIONS[key]}"


def _validate_key(key: str) -> None:
    if key not in SECTIONS:
        raise ValueError(
            f"unknown section: {key!r} (使えるキー: {', '.join(SECTIONS)})"
        )


def _section_range(lines: list[str], key: str) -> tuple[int, int]:
    """見出し行の次の行から、次の見出し (または末尾) までの [start, end) を返す。"""
    _validate_key(key)
    heading = _heading_line(key)
    for i, line in enumerate(lines):
        if line.strip() == heading:
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    end = j
                    break
            return i + 1, end
    raise ValueError(f"section not found in document: {heading}")


def section_items(text: str, key: str) -> list[str]:
    """セクション内の箇条書き ('- ' 始まり) を、先頭の '- ' を除いて返す。"""
    lines = text.splitlines()
    start, end = _section_range(lines, key)
    return [ln[2:].strip() for ln in lines[start:end] if ln.startswith("- ")]


def add_item(text: str, key: str, item: str) -> str:
    """セクションの最後の箇条書きの後ろに item を追記した本文を返す。"""
    item = item.strip()
    if not item:
        raise ValueError("item is empty")
    if "\n" in item:
        raise ValueError("item must be a single line")

    lines = text.splitlines()
    start, end = _section_range(lines, key)

    # セクション内の最後の非空行の直後に挿入する。空なら見出しの直後。
    insert_at = start
    for i in range(start, end):
        if lines[i].strip():
            insert_at = i + 1
    lines.insert(insert_at, f"- {item}")
    return "\n".join(lines) + "\n"


def resolve_open(text: str, index: int) -> str:
    """未決事項の index 番目 (1始まり) を削除した本文を返す。

    決まった内容は別セクションへ add_item で残す。ここでは未決の印を消すだけ。
    """
    lines = text.splitlines()
    start, end = _section_range(lines, "open")
    open_line_nos = [i for i in range(start, end) if lines[i].startswith("- ")]
    if not 1 <= index <= len(open_line_nos):
        raise ValueError(
            f"open item {index} does not exist (未決事項は {len(open_line_nos)} 件)"
        )
    del lines[open_line_nos[index - 1]]
    return "\n".join(lines) + "\n"


def check(text: str) -> list[str]:
    """実装に入れる状態でない理由を返す。空リストなら準備完了。"""
    problems = []
    for key in REQUIRED_FILLED:
        if not section_items(text, key):
            problems.append(f"「{SECTIONS[key]}」が空")
    open_items = section_items(text, "open")
    if open_items:
        problems.append(f"未決事項が {len(open_items)} 件残っている")
    return problems


def _read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{path} がない。先に init を実行する")
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="requirements.md を操作する")
    parser.add_argument("path", type=Path, help="requirements.md のパス")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="空の requirements.md を作る (既存なら失敗)")
    p_init.add_argument("--title", required=True, help="機能・アプリの名前")

    p_add = sub.add_parser("add", help="セクションへ箇条書きを1行追記する")
    p_add.add_argument("section", choices=list(SECTIONS))
    p_add.add_argument("item")

    p_resolve = sub.add_parser("resolve", help="未決事項を1件消す")
    p_resolve.add_argument("index", type=int, help="1始まりの番号")

    sub.add_parser("check", help="実装に入れる状態か判定する (不足があれば終了コード1)")

    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            if args.path.exists():
                raise FileExistsError(f"{args.path} は既にある")
            args.path.parent.mkdir(parents=True, exist_ok=True)
            args.path.write_text(render_template(args.title), encoding="utf-8")
            print(f"created: {args.path}")
        elif args.command == "add":
            new = add_item(_read(args.path), args.section, args.item)
            args.path.write_text(new, encoding="utf-8")
            print(f"added to {SECTIONS[args.section]}")
        elif args.command == "resolve":
            new = resolve_open(_read(args.path), args.index)
            args.path.write_text(new, encoding="utf-8")
            print(f"resolved open item {args.index}")
        else:
            text = _read(args.path)
            for key, heading in SECTIONS.items():
                print(f"{heading}: {len(section_items(text, key))} 件")
            problems = check(text)
            if problems:
                print("\n実装に入れる状態ではない:")
                for p in problems:
                    print(f"- {p}")
                return 1
            print("\n実装に入れる状態")
    except (FileExistsError, FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
