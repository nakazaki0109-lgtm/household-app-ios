"""リリースの現在地(どの段階が済み、次に何をするか)を読み取り専用でまとめる。スキルが次の一手を決めるために使う。"""
from pathlib import Path

from . import session
from .settings import missing_settings
from .stage_state import STAGES, StageState

# Apple ID の認証(2FA・パスワード入力・提出の承認)を伴い、Claude のシェルからは完走できない段階。
INTERACTIVE_STAGES = ["build", "upload", "metadata", "submit"]


def release_status(version: str, state: StageState, settings: dict, home: Path = None) -> dict:
    """version の成功記録が無ければ、全段階を未実施として扱う(fastlane 側の `state begin` と同じ挙動)。"""
    same_version = state.recorded_version() == version
    done = [stage for stage in STAGES if same_version and state.is_done(stage)]
    pending = [stage for stage in STAGES if stage not in done]
    apple_id = str(settings.get("apple_id", "")).strip()
    return {
        "version": version,
        "done": done,
        "pending": pending,
        "next_stage": pending[0] if pending else None,
        "interactive_stages": INTERACTIVE_STAGES,
        "missing_settings": missing_settings(settings, ["apple_id", "team_id"]),
        "login_guidance": session.session_guidance(apple_id, home) if apple_id else None,
    }
