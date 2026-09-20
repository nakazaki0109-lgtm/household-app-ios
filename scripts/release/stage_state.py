"""各段階の成功記録。失敗した段階から再開するために使う。"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import paths

STAGES = ["test", "build", "upload", "screenshots", "metadata", "submit"]

# 段階 -> その結果に依存する段階。前の段階をやり直したら、これらの記録は無効にする。
DEPENDENTS = {
    "test": ["build"],
    "build": ["upload"],
    "upload": ["submit"],
    "screenshots": ["metadata"],
    "metadata": ["submit"],
}

APP_INPUTS = ["HouseholdApp", "HouseholdAppTests", "project.yml"]
STAGE_INPUTS = {
    "test": APP_INPUTS,
    "build": APP_INPUTS,
    "upload": APP_INPUTS,
    "screenshots": APP_INPUTS + ["store/settings.json"],
    "metadata": ["store/metadata", "store/settings.json", "store/app_privacy_details.json",
                "store/review_contact.local.json", "store/screenshots"],
    "submit": ["store/settings.json"],
}


def fingerprint(stage: str, root: Path = paths.ROOT) -> str:
    """段階の入力ファイルの内容ハッシュ。入力が変われば成功記録は使わない。"""
    digest = hashlib.sha256()
    for relative in STAGE_INPUTS[stage]:
        target = Path(root) / relative
        files = sorted(p for p in target.rglob("*") if p.is_file()) if target.is_dir() else [target]
        for file in files:
            if not file.exists() or file.name == ".DS_Store":
                continue
            digest.update(str(file.relative_to(root)).encode())
            digest.update(file.read_bytes())
    return digest.hexdigest()


class StageState:
    def __init__(self, state_file: Path = paths.STATE_FILE, root: Path = paths.ROOT):
        self.state_file = Path(state_file)
        self.root = Path(root)

    def _load(self) -> dict:
        if not self.state_file.exists():
            return {"version": None, "stages": {}}
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def begin(self, version: str) -> None:
        """バージョンが変わったら、前バージョンの記録を捨てる。"""
        data = self._load()
        if data.get("version") != version:
            self._save({"version": version, "stages": {}})

    def is_done(self, stage: str) -> bool:
        record = self._load()["stages"].get(stage)
        return bool(record) and record["fingerprint"] == fingerprint(stage, self.root)

    def get(self, stage: str, key: str):
        record = self._load()["stages"].get(stage)
        return None if not record else record.get("data", {}).get(key)

    def mark_done(self, stage: str, data: dict = None) -> None:
        state = self._load()
        stages = state["stages"]
        stages[stage] = {
            "fingerprint": fingerprint(stage, self.root),
            "at": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        }
        for dependent in self._all_dependents(stage):
            stages.pop(dependent, None)
        self._save(state)

    def reset(self) -> None:
        if self.state_file.exists():
            self.state_file.unlink()

    @staticmethod
    def _all_dependents(stage: str) -> list:
        found = []
        pending = list(DEPENDENTS.get(stage, []))
        while pending:
            current = pending.pop()
            if current not in found:
                found.append(current)
                pending.extend(DEPENDENTS.get(current, []))
        return found
