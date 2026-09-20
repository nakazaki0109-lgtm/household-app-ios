---
name: implementing-requirements
description: "requirements.md の要件を、DDDの思想とSwiftのコンパイル時間を抑える設計で実装する。要件定義が済んだ後に「requirements.md を元に実装して」「要件通りに作って」と言われた時、defining-requirements の後続として実装に入る時に使う。"
---

# Implementing Requirements

`requirements.md` の要件を、抜けなく・要件の範囲を超えずに実装する。Swift のコードは、DDD の層構成とコンパイル時間を抑える規約に沿って書く。

要件を1つずつ「実装した」と言い切れる状態にするのが目的。要件の抜けと作りすぎは、実装した本人には見えないので、番号付きチェックリストと独立したレビューで見つける。

## 進め方

### 1. 実装に入れるか確認する

```bash
python3 .claude/skills/defining-requirements/scripts/requirements_doc.py requirements.md check
```

`実装に入れる状態` と出なければ、defining-requirements に戻る。要件が固まる前に作り始めると、作り直しになるため。`requirements.md` が無い場合も同じ。

### 2. チェックリストを作る

```bash
python3 .claude/skills/implementing-requirements/scripts/requirements_tasks.py requirements.md
```

機能要件 (F)・受け入れ条件 (A)・制約 (C)・スコープ外 (X) に番号が付いて出る。以降は、この番号で「どの要件のための変更か」を指す。`未決事項あり` と出たら、defining-requirements で決めてから戻る。

`requirements.md` は実装中に書き換えない。実装中に要件の曖昧さや矛盾に気づいたら、defining-requirements の `add open` で未決事項に追記し、ユーザーに聞く。実装側で勝手に解釈すると、レビューで検出できなくなる。

### 3. 既存の状態を把握する

README.md、`CONTEXT.md` (あれば)、既存コードの構成を読む。調査が広範囲なら Explore サブエージェントに任せる。要件が既に満たされている部分は、作り直さずチェックリストに済みと記録する。

### 4. 要件を分類して設計する

各 F を「Swift のアプリコード」か「それ以外 (スクリプト、設定、配布)」かに分ける。

- **Swift のアプリコード**: `references/ddd-principles.md` を読み、層への置き場所を決める。新しい用語が出たら domain-modeling で `CONTEXT.md` に確定させてから実装する。コンパイル時間の規約は `references/swift-compile-time.md` を読む。
- **それ以外**: DDD は当てはめず、リポジトリの既存の流儀に従う。決まった処理はテスト付きスクリプトにする (creating-agent-skills の `references/scripts.md` の方針)。

設計が既存の層構成の依存の向きを変える場合、`Models/` の保存項目を変える場合 (データ移行を伴いうる)、`Domain/` のモジュール分割をする場合は、着手前にユーザーへ確認する。戻すのが高コストなため。

### 5. 小さく実装する

要件1つずつ、次の順で進める。

1. 対応する A (受け入れ条件) を、テストにできるものはテストとして先に書く。Domain の不変条件・計算は必ずテストにする。
2. Domain → Models → Services → Views の順に、下の層から実装する。
3. テストを実行して通す。README.md の手順:

   ```bash
   xcodegen generate   # ファイルを追加したとき。.xcodeproj は Git 管理外
   xcodebuild -project HouseholdApp.xcodeproj -scheme HouseholdApp \
     -destination 'platform=iOS Simulator,name=iPhone 16' test
   ```
4. チェックリストの該当項目を済みにする。

スコープ外 (X) に書かれたことは、便利そうでも実装しない。関連する改善を見つけたら、実装せず最終報告に書く。

### 6. コンパイル時間を測る

Swift のコードを変えたときは、`references/swift-compile-time.md` の「計測と、遅い箇所の直し方」に従い、`build_timing.py run` で測って直す。Swift のコードを変えていなければ省く。

### 7. 独立してレビューさせる

`agents/reviewer.md` を読み、その指示に沿ってサブエージェントを1件起動する。渡すもの: チェックリスト (ステップ2の出力)、変更したファイルの一覧、テストと計測の結果、`references/` 2ファイルのパス。

返ってきた指摘のうち、「満たさない」と「重要度: 高」は直して、テストと計測をやり直す。指摘に同意できない場合は、直さない理由を最終報告に書く。

### 8. 報告する

要件の番号ごとに、次のいずれかを報告する。

- 済み: 根拠 (テスト名、確認した挙動)
- 未着手 / 一部のみ: 理由
- 検証不能: 理由 (外部サービスやユーザーの手作業が要るなど)

実行して確かめていない項目を「済み」と書かない。あわせて、スコープ外なので見送った改善、計測で残した遅い箇所、`requirements.md` に追記した未決事項を書く。

## 参照ファイル

- `references/ddd-principles.md` — 層への置き場所の決め方、Aggregate などを導入する条件、用語の扱い。ステップ4で Swift のコードを設計する前に読む
- `references/swift-compile-time.md` — コーディング規約、モジュール分割の条件、計測の使い方。ステップ4・6で読む
- `agents/reviewer.md` — 独立レビューのサブエージェントへの指示。ステップ7で読む
