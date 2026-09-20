"""アプリ名の候補ファイルの読み書き。"""
from pathlib import Path

from . import paths
from .store_rules import LIMITS


def load_candidates(path: Path = paths.NAME_CANDIDATES_FILE) -> list:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def candidate(number: int, path: Path = paths.NAME_CANDIDATES_FILE) -> str:
    """1始まりの番号で候補を返す。範囲外・文字数超過は ValueError。"""
    candidates = load_candidates(path)
    if not 1 <= number <= len(candidates):
        raise ValueError(f"候補{number}はありません（候補は{len(candidates)}件。store/name_candidates.txt に追記してください）")
    name = candidates[number - 1]
    if len(name) > LIMITS["name"]:
        raise ValueError(f"候補{number}「{name}」は{len(name)}文字です（上限{LIMITS['name']}文字）")
    return name


def retry_guidance(number: int, path: Path = paths.NAME_CANDIDATES_FILE) -> str:
    """アプリ名の重複で作成に失敗したときの案内。"""
    remaining = len(load_candidates(path)) - number
    if remaining > 0:
        return f"名前の重複が原因なら、次の候補で再試行できます: fastlane create_app candidate:{number + 1}"
    return "名前の重複が原因なら、候補が残っていません。store/name_candidates.txt に追記してください。"


def apply_name(name: str, metadata_dir: Path = paths.METADATA_DIR) -> None:
    """作成に成功した名前を、ストア情報の name.txt に反映する。"""
    (Path(metadata_dir) / "name.txt").write_text(name + "\n", encoding="utf-8")
