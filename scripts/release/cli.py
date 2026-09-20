"""Fastfile から呼ぶ薄いコマンドライン入口。ロジックは各モジュールに置く。"""
import argparse
import json
import sys

from . import deliver_stage, name_candidates, paths, preflight, screenshots, session, status, store_rules, summary, test_failures
from .settings import load_settings, missing_settings
from .stage_state import STAGES, StageState


def _print_problems(title: str, problems: list) -> int:
    if not problems:
        return 0
    print(title)
    for problem in problems:
        print(f"  ✗ {problem}")
    return 1


def _cmd_validate_metadata(args) -> int:
    return _print_problems("ストア情報の入力ルール違反があります。App Store Connect には反映しません:",
                           store_rules.validate_metadata(paths.METADATA_DIR))


def _cmd_preflight_submit(args) -> int:
    return _print_problems("審査提出の前提が足りません。提出せずに止まります。次を入力・用意してください:",
                           preflight.check_submit())


def _cmd_require_settings(args) -> int:
    return _print_problems("store/settings.local.json に未入力の項目があります:",
                           missing_settings(load_settings(), args.keys))


def _cmd_session_hint(args) -> int:
    message = session.session_guidance(args.apple_id)
    if message:
        print(message)
    return 0


def _cmd_status(args) -> int:
    print(json.dumps(status.release_status(args.version, StageState(), load_settings()), ensure_ascii=False, indent=2))
    return 0


def _cmd_stage_deliver(args) -> int:
    deliver_stage.stage_deliver()
    return 0


def _cmd_summary(args) -> int:
    print(summary.submission_summary(args.version, args.build_number, load_settings(),
                                     paths.METADATA_DIR, paths.SCREENSHOTS_DIR, args.availability))
    return 0


def _cmd_run_tests(args) -> int:
    return test_failures.run_tests(load_settings()["test"]["destination"])


def _cmd_screenshots(args) -> int:
    return screenshots.capture()


def _cmd_name(args) -> int:
    try:
        print(name_candidates.candidate(args.number))
    except ValueError as error:
        print(error)
        return 1
    return 0


def _cmd_name_retry(args) -> int:
    print(name_candidates.retry_guidance(args.number))
    return 0


def _cmd_name_apply(args) -> int:
    name_candidates.apply_name(name_candidates.candidate(args.number))
    return 0


def _cmd_state(args) -> int:
    state = StageState()
    action, first, second = args.action, args.first, args.second
    if action == "begin":
        state.begin(first)
        return 0
    if action == "reset":
        state.reset()
        return 0
    if first not in STAGES:
        print(f"段階名は {', '.join(STAGES)} のいずれかです: {first}")
        return 2
    if action == "is-done":
        return 0 if state.is_done(first) else 1
    if action == "mark":
        state.mark_done(first, json.loads(second) if second else {})
        return 0
    value = state.get(first, second)
    if value is None:
        return 1
    print(value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="release")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, func in [("validate-metadata", _cmd_validate_metadata), ("preflight-submit", _cmd_preflight_submit),
                       ("stage-deliver", _cmd_stage_deliver), ("run-tests", _cmd_run_tests),
                       ("screenshots", _cmd_screenshots)]:
        sub.add_parser(name).set_defaults(func=func)

    require = sub.add_parser("require-settings")
    require.add_argument("keys", nargs="+")
    require.set_defaults(func=_cmd_require_settings)

    hint = sub.add_parser("session-hint")
    hint.add_argument("apple_id")
    hint.set_defaults(func=_cmd_session_hint)

    stat = sub.add_parser("status")
    stat.add_argument("version")
    stat.set_defaults(func=_cmd_status)

    summ = sub.add_parser("summary")
    summ.add_argument("version")
    summ.add_argument("build_number")
    summ.add_argument("availability", nargs="?", default="manual")
    summ.set_defaults(func=_cmd_summary)

    for name, func in [("name", _cmd_name), ("name-retry", _cmd_name_retry), ("name-apply", _cmd_name_apply)]:
        cmd = sub.add_parser(name)
        cmd.add_argument("number", type=int)
        cmd.set_defaults(func=func)

    state = sub.add_parser("state")
    state.add_argument("action", choices=["begin", "reset", "is-done", "mark", "get"])
    state.add_argument("first", nargs="?")
    state.add_argument("second", nargs="?")
    state.set_defaults(func=_cmd_state)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
