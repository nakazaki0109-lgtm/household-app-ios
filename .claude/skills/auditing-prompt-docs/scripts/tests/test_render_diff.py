from pathlib import Path

from scripts.render_diff import render_diff


def test_render_diff_shows_changed_line(tmp_path):
    original = tmp_path / "original.md"
    proposed = tmp_path / "proposed.md"
    original.write_text("line one\nline two\nline three\n", encoding="utf-8")
    proposed.write_text("line one\nline TWO\nline three\n", encoding="utf-8")

    diff = render_diff(original, proposed)

    assert "-line two" in diff
    assert "+line TWO" in diff


def test_render_diff_empty_when_identical(tmp_path):
    original = tmp_path / "a.md"
    proposed = tmp_path / "b.md"
    content = "same content\n"
    original.write_text(content, encoding="utf-8")
    proposed.write_text(content, encoding="utf-8")

    assert render_diff(original, proposed) == ""


def test_render_diff_does_not_modify_files(tmp_path):
    original = tmp_path / "a.md"
    proposed = tmp_path / "b.md"
    original.write_text("before\n", encoding="utf-8")
    proposed.write_text("after\n", encoding="utf-8")

    render_diff(original, proposed)

    assert original.read_text(encoding="utf-8") == "before\n"
    assert proposed.read_text(encoding="utf-8") == "after\n"


def test_render_diff_respects_context_lines(tmp_path):
    original = tmp_path / "a.md"
    proposed = tmp_path / "b.md"
    lines = [f"l{i}" for i in range(20)]
    original.write_text("\n".join(lines) + "\n", encoding="utf-8")
    lines[10] = "CHANGED"
    proposed.write_text("\n".join(lines) + "\n", encoding="utf-8")

    diff_wide = render_diff(original, proposed, context_lines=5)
    diff_narrow = render_diff(original, proposed, context_lines=1)

    assert len(diff_wide.splitlines()) > len(diff_narrow.splitlines())
