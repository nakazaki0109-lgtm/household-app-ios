import pytest

from scripts import review_scope
from scripts.review_scope import (
    Change,
    Violation,
    find_import_violations,
    main,
    merge_changes,
    parse_name_status,
    parse_untracked,
    render_report,
)


def test_parse_name_status_handles_add_modify_delete_and_rename():
    text = "A\tApp/Domain/Money.swift\nM\tApp/Views/A.swift\nD\told.swift\nR100\tbefore.swift\tafter.swift\n"

    assert parse_name_status(text) == [
        Change("App/Domain/Money.swift", "A"),
        Change("App/Views/A.swift", "M"),
        Change("old.swift", "D"),
        Change("after.swift", "R"),
    ]


def test_parse_name_status_ignores_blank_and_malformed_lines():
    assert parse_name_status("\n\nnonsense\n") == []


def test_parse_untracked_marks_status_U():
    assert parse_untracked("a.swift\n\nb.md\n") == [Change("a.swift", "U"), Change("b.md", "U")]


def test_merge_changes_dedupes_by_path_preferring_later_and_sorts():
    merged = merge_changes([Change("b", "M"), Change("a", "M")], [Change("b", "D")])

    assert merged == [Change("a", "M"), Change("b", "D")]


@pytest.mark.parametrize(
    "path,layer",
    [
        ("HouseholdApp/Domain/Money.swift", "Domain"),
        ("HouseholdApp/Models/Category.swift", "Models"),
        ("HouseholdApp/Services/BudgetService.swift", "Services"),
        ("HouseholdApp/Views/Budgets/MonthlyBudgetEditView.swift", "Views"),
        ("HouseholdApp/App/HouseholdAppApp.swift", None),
        ("HouseholdAppTests/DomainTests.swift", None),
        ("scripts/Domain/tool.py", None),
    ],
)
def test_layer_classification(path, layer):
    assert Change(path, "M").layer == layer


def test_test_files_are_recognised():
    assert Change("HouseholdAppTests/ServiceTests.swift", "M").is_test
    assert not Change("HouseholdApp/Domain/Money.swift", "M").is_test


def test_domain_importing_swiftui_and_swiftdata_is_flagged():
    change = Change("HouseholdApp/Domain/Money.swift", "M")
    content = "import Foundation\nimport SwiftUI\nimport SwiftData\n"

    assert find_import_violations(change, content) == [
        Violation(change.path, "Domain", "SwiftUI"),
        Violation(change.path, "Domain", "SwiftData"),
    ]


def test_allowed_imports_are_not_flagged():
    assert find_import_violations(Change("HouseholdApp/Domain/Money.swift", "M"), "import Foundation\n") == []
    assert find_import_violations(Change("HouseholdApp/Services/A.swift", "M"), "import SwiftData\n") == []
    assert find_import_violations(Change("HouseholdApp/Views/A.swift", "M"), "import SwiftUI\nimport SwiftData\n") == []


def test_import_forms_with_attributes_and_kinds_are_detected():
    change = Change("HouseholdApp/Services/A.swift", "M")

    assert find_import_violations(change, "@testable import SwiftUI\n")
    assert find_import_violations(change, "import struct SwiftUI.Color\n")


def test_commented_out_import_is_not_flagged():
    change = Change("HouseholdApp/Domain/Money.swift", "M")

    assert find_import_violations(change, "// import SwiftUI\n") == []


def test_non_swift_and_test_files_are_never_flagged():
    assert find_import_violations(Change("tool.py", "M"), "import SwiftUI\n") == []
    assert find_import_violations(Change("HouseholdAppTests/A.swift", "M"), "import SwiftUI\n") == []


def test_render_report_no_changes():
    assert "変更はありません" in render_report([], [], False, "作業ツリー")


def test_render_report_lists_files_layers_and_violations():
    changes = [Change("HouseholdApp/Domain/Money.swift", "M"), Change("README.md", "U")]
    violations = [Violation("HouseholdApp/Domain/Money.swift", "Domain", "SwiftUI")]

    report = render_report(changes, violations, True, "作業ツリー")

    assert "変更ファイル: 2 件 (うち Swift のアプリコード 1 件)" in report
    assert "[変更] HouseholdApp/Domain/Money.swift (Domain)" in report
    assert "[未追跡] README.md (-)" in report
    assert "Domain 層が SwiftUI を import している" in report
    assert "requirements.md: あり" in report


def test_main_reports_violation_from_files_on_disk(tmp_path, monkeypatch, capsys):
    domain = tmp_path / "HouseholdApp" / "Domain"
    domain.mkdir(parents=True)
    (domain / "Bad.swift").write_text("import SwiftUI\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        review_scope, "collect_changes", lambda base: ([Change("HouseholdApp/Domain/Bad.swift", "U")], "テスト")
    )

    assert main([]) == 1
    assert "Domain 層が SwiftUI" in capsys.readouterr().out


def test_main_skips_deleted_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(review_scope, "collect_changes", lambda base: ([Change("HouseholdApp/Domain/Gone.swift", "D")], "テスト"))

    assert main([]) == 0


def test_main_returns_2_when_git_fails(monkeypatch, capsys):
    def boom(base):
        raise RuntimeError("git diff に失敗しました: bad revision")

    monkeypatch.setattr(review_scope, "collect_changes", boom)

    assert main(["--base", "nope"]) == 2
    assert "bad revision" in capsys.readouterr().err
