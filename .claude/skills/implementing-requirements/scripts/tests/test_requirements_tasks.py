import json

from scripts.requirements_tasks import main, parse_sections, render_markdown

SAMPLE = """# 家計簿 要件定義

## 目的と対象ユーザー
- 個人利用

## 機能要件
- 収支を登録できる
- 月別に集計できる

## 受け入れ条件
- 負の金額は登録できない

## 制約・非機能要件
- iOS 17 以上

## スコープ外（やらないこと）
- 編集UI

## 未決事項
"""


def test_parse_sections_assigns_sequential_ids():
    sections = parse_sections(SAMPLE)

    assert sections["functional"] == [
        {"id": "F1", "text": "収支を登録できる"},
        {"id": "F2", "text": "月別に集計できる"},
    ]
    assert sections["acceptance"] == [{"id": "A1", "text": "負の金額は登録できない"}]
    assert sections["constraints"][0]["id"] == "C1"
    assert sections["out_of_scope"][0]["id"] == "X1"


def test_parse_sections_ignores_untargeted_sections():
    sections = parse_sections(SAMPLE)

    all_texts = [i["text"] for items in sections.values() for i in items]
    assert "個人利用" not in all_texts


def test_parse_sections_missing_sections_are_empty():
    sections = parse_sections("# x\n")

    assert all(items == [] for items in sections.values())


def test_render_markdown_lists_checkboxes_and_no_open_warning():
    md = render_markdown(parse_sections(SAMPLE))

    assert "- [ ] F1: 収支を登録できる" in md
    assert "- [ ] A1: 負の金額は登録できない" in md
    assert "未決事項あり" not in md


def test_render_markdown_warns_when_open_items_exist():
    text = SAMPLE + "- 予算超過時の通知\n"

    md = render_markdown(parse_sections(text))

    assert md.startswith("## 未決事項あり")
    assert "O1: 予算超過時の通知" in md


def test_main_prints_checklist(tmp_path, capsys):
    path = tmp_path / "requirements.md"
    path.write_text(SAMPLE, encoding="utf-8")

    assert main([str(path)]) == 0
    assert "F2: 月別に集計できる" in capsys.readouterr().out


def test_main_json_output(tmp_path, capsys):
    path = tmp_path / "requirements.md"
    path.write_text(SAMPLE, encoding="utf-8")

    assert main([str(path), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["functional"][0]["id"] == "F1"


def test_main_fails_when_file_missing(tmp_path, capsys):
    assert main([str(tmp_path / "nope.md")]) == 1
    assert "defining-requirements" in capsys.readouterr().err


def test_main_fails_when_no_functional_requirements(tmp_path, capsys):
    path = tmp_path / "requirements.md"
    path.write_text("# x\n\n## 機能要件\n", encoding="utf-8")

    assert main([str(path)]) == 1
    assert "機能要件" in capsys.readouterr().err
