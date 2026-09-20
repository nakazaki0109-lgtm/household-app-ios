---
name: defining-requirements
description: "曖昧な要件を、実装に入れる仕様になるまでプロダクトマネージャー役の質問で詰め、決まったことを requirements.md に残す。新機能・アプリ・改修の依頼が曖昧なまま実装に入りそうな時、「要件を整理したい」「仕様を詰めたい」「何を作るか決めたい」と言われた時、作り始める前に抜けを洗い出したい時に使う。"
---

# Defining Requirements

プロダクトマネージャー役として、ユーザーの曖昧な依頼を選択式の質問で詰め、実装に入れる粒度の仕様にして `requirements.md` に残す。

依頼した本人には、自分の要件の抜けが見えない。質問される側に回ると抜けが埋まる。作ってから「こうじゃない」が出るより、作る前に聞くほうがずっと安い。

## 進め方

### 1. 下調べをする

質問する前に、調べられることは自分で調べる。README、既存コード、`CONTEXT.md`、既存の `requirements.md` を読む。コードを見れば分かることをユーザーに聞くと、質問の価値が下がるうえ、ユーザーの手間が増える。調査が広範囲に及ぶ場合は Explore サブエージェントに任せる。

### 2. requirements.md を用意する

置き場所は、ユーザーの指定がなければリポジトリ直下の `requirements.md`。既にあれば内容を読み、続きから再開する（上書きしない）。なければ作る:

```bash
python3 .claude/skills/defining-requirements/scripts/requirements_doc.py requirements.md init --title "<機能・アプリの名前>"
```

書式を毎回考えないために、作成・追記・確認はすべてこのスクリプトで行う。セクションは `purpose` `in-scope` `out-of-scope` `functional` `acceptance` `constraints` `open` の7つ。

### 3. 質問する

質問の作り方は `references/interview-method.md` を読んで従う。要点だけ挙げる:

- 一度に聞くのは1〜3問。答えを聞いてから次の質問を組み立て直す（先の質問は、前の答えで変わるため）
- AskUserQuestion で選択式にし、推奨案を先頭に置いて理由を添える
- 最初は「誰が、どんな痛みを消したいか」から入る

### 4. 決まったことをすぐ書く

答えをもらうたびに、まとめずにその場で追記する。書き忘れや、会話が長引いたときの取りこぼしを防ぐため。

```bash
python3 .claude/skills/defining-requirements/scripts/requirements_doc.py requirements.md add <セクション> "<1行の内容>"
```

「まだ決められない」と言われた項目は `open` に追記する。後で決まったら、決まった内容を該当セクションへ `add` してから `resolve <番号>` で `open` から消す。

### 5. 終わりを判定する

質問が尽きたと思ったら、次を実行する。

```bash
python3 .claude/skills/defining-requirements/scripts/requirements_doc.py requirements.md check
```

`実装に入れる状態` と出たら、`requirements.md` の内容をユーザーに見せて、認識が合っているか確認する。不足が出たら、その不足を埋める質問に戻る。

ユーザーが確認するまで、実装には着手しない。要件の認識合わせが済む前に作り始めると、このスキルを使う意味がなくなるため。

## 参照ファイル

- `references/interview-method.md` — 質問を組み立てる段階（決定木の辿り方、質問の順序、選択肢の作り方、記録の書き方）。質問を作る前に読む
