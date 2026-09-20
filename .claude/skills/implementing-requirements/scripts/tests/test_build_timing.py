from scripts.build_timing import SlowSpot, build_command, main, parse_log, render_report

LOG = """\
CompileSwift normal arm64 /p/Foo.swift
/p/Foo.swift:12:8: warning: instance method 'bar()' took 312ms to type-check (limit: 200ms)
/p/Views/A.swift:30:5: warning: expression took 150ms to type-check (limit: 100ms)
/p/Foo.swift:12:8: warning: instance method 'bar()' took 400ms to type-check (limit: 200ms)
/p/Foo.swift:3:1: warning: unused variable 'x'
** BUILD SUCCEEDED **
"""


def test_parse_log_sorts_slowest_first_and_dedupes_by_max():
    spots = parse_log(LOG)

    assert spots == [
        SlowSpot("/p/Foo.swift", 12, "instance method 'bar()'", 400),
        SlowSpot("/p/Views/A.swift", 30, "expression", 150),
    ]


def test_parse_log_ignores_unrelated_warnings():
    assert parse_log("/p/Foo.swift:3:1: warning: unused variable 'x'\n") == []


def test_is_expression():
    assert SlowSpot("f", 1, "expression", 1).is_expression
    assert not SlowSpot("f", 1, "global function 'g()'", 1).is_expression


def test_build_command_enables_both_warnings_and_cleans():
    cmd = build_command("A.xcodeproj", "A", "generic/platform=iOS Simulator", 200, 100)

    flags = next(a for a in cmd if a.startswith("OTHER_SWIFT_FLAGS="))
    assert "-warn-long-function-bodies=200" in flags
    assert "-warn-long-expression-type-checking=100" in flags
    assert cmd[-2:] == ["clean", "build"]


def test_render_report_empty():
    assert "ありません" in render_report([], top=10)


def test_render_report_respects_top_and_labels_kind():
    report = render_report(parse_log(LOG), top=1)

    assert "上位 1 件" in report
    assert "400ms [関数]" in report
    assert "[式]" not in report


def test_main_parse_returns_1_when_slow_spots_found(tmp_path, capsys):
    log = tmp_path / "build.log"
    log.write_text(LOG, encoding="utf-8")

    assert main(["parse", str(log)]) == 1
    assert "400ms" in capsys.readouterr().out


def test_main_parse_returns_0_when_clean(tmp_path):
    log = tmp_path / "build.log"
    log.write_text("** BUILD SUCCEEDED **\n", encoding="utf-8")

    assert main(["parse", str(log)]) == 0
