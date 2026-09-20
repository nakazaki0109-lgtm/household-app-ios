from pathlib import Path

from scripts.find_prompt_docs import find_prompt_docs


def _touch(path: Path, content: str = "dummy") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_finds_default_target_names(tmp_path):
    _touch(tmp_path / "CLAUDE.md")
    _touch(tmp_path / "sub" / "AGENTS.md")
    _touch(tmp_path / ".claude" / "skills" / "foo" / "SKILL.md")
    _touch(tmp_path / "README.md")  # 対象外

    found = find_prompt_docs(tmp_path)

    assert found == sorted(
        [
            tmp_path / "CLAUDE.md",
            tmp_path / "sub" / "AGENTS.md",
            tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        ]
    )


def test_excludes_default_excluded_dirs(tmp_path):
    _touch(tmp_path / "node_modules" / "pkg" / "SKILL.md")
    _touch(tmp_path / "Pods" / "SKILL.md")
    _touch(tmp_path / "CLAUDE.md")

    found = find_prompt_docs(tmp_path)

    assert found == [tmp_path / "CLAUDE.md"]


def test_custom_target_names(tmp_path):
    _touch(tmp_path / "NOTES.md")
    _touch(tmp_path / "CLAUDE.md")

    found = find_prompt_docs(tmp_path, target_names=("NOTES.md",))

    assert found == [tmp_path / "NOTES.md"]


def test_returns_empty_list_when_nothing_found(tmp_path):
    _touch(tmp_path / "README.md")
    assert find_prompt_docs(tmp_path) == []
