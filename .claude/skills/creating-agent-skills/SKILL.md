---
name: creating-agent-skills
description: Claude Codeのスキル（SKILL.md）を新規作成する、または既存スキルを観点別にレビューして改善案を出す。サブエージェント設計をスキル内に閉じ込める、決まった処理はテスト付きスクリプトに任せる、SKILL.md本体は参照ファイルに分割する、という設計方針に基づく。ユーザーが「スキルを作りたい」「この作業をスキルにしたい」「既存スキルを見直したい/改善したい」「SKILL.mdの書き方を知りたい」と言ったときに使う。
---

# スキルを作るスキル

Claude Codeのスキルを作る/直すときの一貫した型を提供する。素のAnthropic公式 skill-creator を土台にしつつ、次の4点を重視する:

1. サブエージェントを使うなら、その設計は `agents/*.md` としてスキルの中に閉じ込める
2. 決まった処理は Python/Bash スクリプトに任せる（モデルに毎回考えさせない）
3. `SKILL.md` 本体には詰め込まず、詳細は `references/*.md` に切り出す
4. スクリプトには pytest の単体テストを書く

このスキル自身も同じ方針で作られている。`scripts/scaffold_skill.py` とその単体テスト `scripts/tests/test_scaffold_skill.py` が実例であり、本文はこのファイルだけで完結させず `references/` に分割してある。

## モードを見極める

ユーザーの依頼が次のどちらかを判断する。

- **新規作成**: まだ存在しないスキルを作りたい → 「新しいスキルを作る」へ
- **既存スキルのレビュー/改善**: 既にある `SKILL.md` を良くしたい → 「既存スキルをレビューする」へ

迷う場合は聞く。

---

## 新しいスキルを作る

### 1. インタビューする

次を聞く（会話の中に既に答えがあれば聞き直さない）:

- このスキルはClaudeに何をさせたいか
- いつ発火してほしいか（ユーザーのどんな発言・状況で使われるべきか）
- 期待する出力の形
- サブエージェントを使う必要がありそうか（並列に独立した作業をさせたい、独立した視点での採点/比較をさせたい、など）
- 決まりきった処理（雛形生成、採番、集計、フォーマット変換、検証など）が含まれそうか

### 2. 解剖図を確認する

`references/anatomy.md` を読み、`SKILL.md` / `references/` / `scripts/` / `agents/` の役割分担とprogressive disclosureの考え方を踏まえる。すべてのディレクトリを機械的に作る必要はなく、そのスキルに実際に要るものだけを作る。

### 3. 雛形を作る

ディレクトリ作成という決まった処理は `scripts/scaffold_skill.py` に任せる。

```bash
python .claude/skills/creating-agent-skills/scripts/scaffold_skill.py \
  <配置先ディレクトリ> <スキル名> \
  [--description "..."] [--with-scripts] [--with-agents] [--with-references]
```

- `<配置先ディレクトリ>`: 通常はプロジェクトの `.claude/skills`
- `<スキル名>`: kebab-case
- サブエージェントを使う設計なら `--with-agents`、決まった処理をスクリプト化するなら `--with-scripts`、詳細を切り出す予定なら `--with-references` を付ける

### 4. SKILL.md 本文を書く

- `description` には「何をするか」と「いつ使うべきか」の両方を、具体的なトリガー文脈込みで書く。曖昧な一文で済ませない
- 本文は指示形で書き、"MUST" のような命令だけでなく理由（なぜそうすべきか）も添える
- 500行に近づいたら `references/anatomy.md` の「SKILL.mdが肥大化してきたら」に従って分割する

### 5. サブエージェントを使うなら設計を閉じ込める

`references/subagents.md` を読み、`agents/<役割>.md` に役割・入力・出力・制約を書く。SKILL.md本文には「いつこのagentファイルを読んでサブエージェントを飛ばすか」だけを書き、指示の本体は埋め込まない。

### 6. 決まった処理はスクリプト化してテストを書く

`references/scripts.md` を読み、`scripts/` にスクリプト、`scripts/tests/` に pytest のユニットテストを書く。CLIのエントリポイントとロジック本体を分離し、ロジック本体を直接テストできる形にする。書いたら実際に実行して確認する:

```bash
cd <スキルのディレクトリ>
python -m pytest scripts/tests
```

### 7. 仕上げのセルフチェック

`references/review-checklist.md` の観点を、自分が今書いたスキルにそのまま当てて一通り確認してから完成とする。

---

## 既存スキルをレビューする

1. 対象の `SKILL.md`（と同梱の `references/` `scripts/` `agents/`）を読む
2. `references/review-checklist.md` の観点ごとに現状を確認し、「現状 → 提案」を1行ずつまとめる。問題がない観点は無理に指摘を作らず「問題なし」と書く
3. まとめた提案をユーザーに提示し、適用してよいか確認する
4. 適用の合意が取れた項目だけ実際に編集する。スクリプトを追加・変更した場合は必ず対応するテストを書き、`python -m pytest scripts/tests` で通ることを確認する

## 参照ファイル

- `references/anatomy.md` — ディレクトリ構成とprogressive disclosureの考え方、SKILL.mdが肥大化したときの分割方法
- `references/subagents.md` — サブエージェント設計を `agents/*.md` に閉じ込める理由とテンプレート
- `references/scripts.md` — どんな処理をスクリプト化すべきか、置き場所、pytestでのテストの書き方
- `references/review-checklist.md` — 既存スキルをレビューする際の観点と出力フォーマット
