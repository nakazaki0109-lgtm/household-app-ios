from scripts.release.store_rules import validate_metadata


def write_metadata(tmp_path, **fields):
    for name, text in fields.items():
        (tmp_path / f"{name}.txt").write_text(text, encoding="utf-8")


def valid(**overrides):
    fields = {"name": "家計簿", "subtitle": "サブ", "description": "説明", "keywords": "a,b"}
    fields.update(overrides)
    return fields


def test_valid_metadata_has_no_violations(tmp_path):
    write_metadata(tmp_path, **valid())
    assert validate_metadata(tmp_path) == []


def test_description_over_limit_reports_item_and_excess(tmp_path):
    write_metadata(tmp_path, **valid(description="あ" * 4005))
    assert validate_metadata(tmp_path) == ["description: 4005文字 (上限4000文字、5文字超過)"]


def test_limit_counts_characters_not_bytes(tmp_path):
    write_metadata(tmp_path, **valid(name="あ" * 30, subtitle="あ" * 30))
    assert validate_metadata(tmp_path) == []


def test_trailing_newline_is_not_counted(tmp_path):
    write_metadata(tmp_path, **valid(name=("あ" * 30) + "\n"))
    assert validate_metadata(tmp_path) == []


def test_multiple_violations_are_all_reported(tmp_path):
    write_metadata(tmp_path, **valid(name="あ" * 31, keywords="k" * 101))
    violations = validate_metadata(tmp_path)
    assert "name: 31文字 (上限30文字、1文字超過)" in violations
    assert "keywords: 101文字 (上限100文字、1文字超過)" in violations


def test_missing_required_field_is_a_violation(tmp_path):
    write_metadata(tmp_path, **valid())
    (tmp_path / "keywords.txt").unlink()
    assert validate_metadata(tmp_path) == ["keywords: 未入力です (keywords.txt)"]


def test_optional_field_may_be_absent_but_is_limited_when_present(tmp_path):
    write_metadata(tmp_path, **valid(promotional_text="あ" * 171))
    assert validate_metadata(tmp_path) == ["promotional_text: 171文字 (上限170文字、1文字超過)"]
