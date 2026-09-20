"""App Store Connect の入力ルール (文字数など) の検査。"""
from pathlib import Path

LIMITS = {
    "name": 30,
    "subtitle": 30,
    "keywords": 100,
    "description": 4000,
    "promotional_text": 170,
}
REQUIRED = ["name", "subtitle", "description", "keywords"]


def read_field(metadata_dir: Path, field: str) -> str:
    """メタデータ1項目を読む。末尾の改行・空白は文字数に数えない。"""
    path = Path(metadata_dir) / f"{field}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def validate_metadata(metadata_dir: Path) -> list:
    """違反を「項目名: 内容」の文字列で返す。空なら問題なし。"""
    violations = []
    for field, limit in LIMITS.items():
        text = read_field(metadata_dir, field)
        if not text:
            if field in REQUIRED:
                violations.append(f"{field}: 未入力です ({field}.txt)")
            continue
        length = len(text)
        if length > limit:
            over = length - limit
            violations.append(f"{field}: {length}文字 (上限{limit}文字、{over}文字超過)")
    return violations
