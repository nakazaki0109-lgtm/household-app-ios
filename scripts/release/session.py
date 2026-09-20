"""Apple ID セッション Cookie の状態案内。中身は読まず、ファイルの有無と更新日時だけを見る。"""
import time
from pathlib import Path

SESSION_DAYS = 30


def cookie_path(apple_id: str, home: Path = None) -> Path:
    return Path(home or Path.home()) / ".fastlane" / "spaceship" / apple_id / "cookie"


def session_guidance(apple_id: str, home: Path = None, now: float = None):
    """2FA が求められそうなときだけ案内文を返す。有効そうなら None。"""
    path = cookie_path(apple_id, home)
    if not path.exists():
        return "セッション Cookie がありません。2段階認証のコードが求められるので、ターミナルに入力してください（入力後は同じ段階が続行されます）。"
    age_days = ((now or time.time()) - path.stat().st_mtime) / 86400
    if age_days > SESSION_DAYS:
        return ("セッション Cookie が期限切れの可能性があります。"
                "2段階認証のコードが求められたら、ターミナルに入力してください（入力後は同じ段階が続行されます）。")
    return None
