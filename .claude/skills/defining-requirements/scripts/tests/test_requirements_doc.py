import pytest

from scripts.requirements_doc import (
    SECTIONS,
    add_item,
    check,
    main,
    render_template,
    resolve_open,
    section_items,
)


def test_render_template_has_all_sections_in_order():
    text = render_template("家計簿")

    assert text.startswith("# 家計簿 要件定義")
    positions = [text.index(f"## {h}") for h in SECTIONS.values()]
    assert positions == sorted(positions)


def test_add_item_appends_after_last_item():
    text = render_template("x")
    text = add_item(text, "functional", "収支を登録できる")
    text = add_item(text, "functional", "月別に集計できる")

    assert section_items(text, "functional") == ["収支を登録できる", "月別に集計できる"]


def test_add_item_does_not_leak_into_other_sections():
    text = add_item(render_template("x"), "functional", "A")

    assert section_items(text, "acceptance") == []
    assert section_items(text, "open") == []


def test_add_item_to_last_section_works():
    text = add_item(render_template("x"), "open", "予算超過時の通知はどうするか")

    assert section_items(text, "open") == ["予算超過時の通知はどうするか"]


@pytest.mark.parametrize("item", ["", "   ", "1行目\n2行目"])
def test_add_item_rejects_empty_or_multiline(item):
    with pytest.raises(ValueError):
        add_item(render_template("x"), "functional", item)


def test_add_item_rejects_unknown_section():
    with pytest.raises(ValueError):
        add_item(render_template("x"), "nope", "A")


def test_add_item_fails_when_heading_missing():
    with pytest.raises(ValueError):
        add_item("# 見出しなし\n", "functional", "A")


def test_resolve_open_removes_nth_item_only():
    text = render_template("x")
    for q in ["Q1", "Q2", "Q3"]:
        text = add_item(text, "open", q)

    text = resolve_open(text, 2)

    assert section_items(text, "open") == ["Q1", "Q3"]


@pytest.mark.parametrize("index", [0, 3, -1])
def test_resolve_open_rejects_out_of_range(index):
    text = add_item(add_item(render_template("x"), "open", "Q1"), "open", "Q2")

    with pytest.raises(ValueError):
        resolve_open(text, index)


def _ready_doc():
    text = render_template("x")
    text = add_item(text, "purpose", "個人の支出を把握する")
    text = add_item(text, "functional", "収支を登録できる")
    text = add_item(text, "acceptance", "登録後、一覧に即反映される")
    text = add_item(text, "out-of-scope", "複数端末での同期")
    return text


def test_check_passes_for_ready_doc():
    assert check(_ready_doc()) == []


def test_check_reports_empty_required_sections():
    problems = check(render_template("x"))

    assert len(problems) == 4
    assert any("機能要件" in p for p in problems)


def test_check_reports_remaining_open_items():
    text = add_item(_ready_doc(), "open", "Q1")

    problems = check(text)

    assert problems == ["未決事項が 1 件残っている"]


def test_main_init_add_check_flow(tmp_path, capsys):
    path = tmp_path / "docs" / "requirements.md"

    assert main([str(path), "init", "--title", "家計簿"]) == 0
    assert main([str(path), "add", "functional", "収支を登録できる"]) == 0
    assert main([str(path), "check"]) == 1  # まだ不足あり
    assert "収支を登録できる" in path.read_text(encoding="utf-8")


def test_main_init_refuses_to_overwrite(tmp_path, capsys):
    path = tmp_path / "requirements.md"
    path.write_text("既存の内容", encoding="utf-8")

    assert main([str(path), "init", "--title", "x"]) == 1
    assert path.read_text(encoding="utf-8") == "既存の内容"


def test_main_add_without_init_fails(tmp_path):
    assert main([str(tmp_path / "requirements.md"), "add", "functional", "A"]) == 1
