#!/usr/bin/env python3
"""新しい Claude Code スキルのディレクトリ雛形を作る。

決まりきったディレクトリ作成・SKILL.md 冒頭の frontmatter 生成はモデルに
毎回考えさせず、このスクリプトに任せる。名前の妥当性チェックやファイル
配置のロジックはここに集約し、pytest でテストする
(tests/test_scaffold_skill.py)。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

SKILL_MD_TEMPLATE = """---
name: {name}
description: "{description}"
---

# {title}

<!--
  本体には詰め込みすぎない。
  - 決まった処理は scripts/ に書いてスクリプトに任せる
  - サブエージェントに渡す指示は agents/ に切り出す
  - 詳細な参照情報は references/ に切り出し、いつ読むかを本体から明記する
-->
"""

REFERENCE_EXAMPLE = """# 参照ファイルの例

SKILL.md の本体に詰め込まず、詳細はここに書く。
SKILL.md 側からは「どんな時にこのファイルを読むか」を一文で示して参照する。
"""

AGENT_EXAMPLE = """# サブエージェントへの指示（例）

## 役割
TODO: このサブエージェントが何を担当するか

## 入力
TODO: 呼び出し元のスキルが渡すもの（パス、パラメータなど）

## 出力
TODO: 何を、どこに、どの形式で返すか

## 制約
TODO: やってはいけないこと（例: ユーザーに質問しない、呼び出し元の文脈を勝手に推測しない）
"""


def slug_to_title(name: str) -> str:
    """kebab-case のスキル名を見出し用のタイトルに変換する。"""
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_name(name: str) -> None:
    if not NAME_RE.match(name):
        raise ValueError(
            f"invalid skill name: {name!r} (kebab-case の英数字のみ使用可能)"
        )


def scaffold_skill(
    parent_dir: Path,
    name: str,
    *,
    with_scripts: bool = False,
    with_agents: bool = False,
    with_references: bool = False,
    description: str = "TODO: このスキルが何をするか、いつ使うべきかを書く",
) -> Path:
    """parent_dir/name にスキルの雛形を作り、そのパスを返す。

    既に同名のディレクトリがあれば FileExistsError を送出する
    (既存スキルを誤って上書きしないため)。
    """
    validate_name(name)

    skill_dir = Path(parent_dir) / name
    if skill_dir.exists():
        raise FileExistsError(f"skill directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True)
    skill_md = SKILL_MD_TEMPLATE.format(
        name=name, description=description, title=slug_to_title(name)
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    if with_references:
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "example.md").write_text(REFERENCE_EXAMPLE, encoding="utf-8")

    if with_scripts:
        scripts_dir = skill_dir / "scripts"
        tests_dir = scripts_dir / "tests"
        tests_dir.mkdir(parents=True)
        (scripts_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        test_stub_name = f"test_{name.replace('-', '_')}.py"
        (tests_dir / test_stub_name).write_text(
            "# TODO: scripts/ に置いたスクリプトの純粋なロジックに対する\n"
            "# pytest ユニットテストを書く。\n"
            "#\n"
            "# from scripts.my_script import do_something\n"
            "#\n"
            "# def test_do_something():\n"
            "#     assert do_something(1, 2) == 3\n",
            encoding="utf-8",
        )

    if with_agents:
        agents_dir = skill_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "example.md").write_text(AGENT_EXAMPLE, encoding="utf-8")

    return skill_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Claude Code スキルのディレクトリ雛形を作成する"
    )
    parser.add_argument(
        "parent_dir", type=Path, help="作成先の親ディレクトリ (例: .claude/skills)"
    )
    parser.add_argument("name", help="スキル名 (kebab-case)")
    parser.add_argument("--description", default=None, help="frontmatter の description")
    parser.add_argument(
        "--with-scripts", action="store_true", help="scripts/ と scripts/tests/ を作成する"
    )
    parser.add_argument("--with-agents", action="store_true", help="agents/ を作成する")
    parser.add_argument(
        "--with-references", action="store_true", help="references/ を作成する"
    )
    args = parser.parse_args(argv)

    kwargs = {}
    if args.description:
        kwargs["description"] = args.description

    try:
        skill_dir = scaffold_skill(
            args.parent_dir,
            args.name,
            with_scripts=args.with_scripts,
            with_agents=args.with_agents,
            with_references=args.with_references,
            **kwargs,
        )
    except (FileExistsError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"created: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
