---
name: releasing-to-app-store
description: "fastlane（scripts/release）で、テスト→ビルド→TestFlightアップロード→スクリーンショット→ストア情報反映→審査提出のリリースを進める。今どこまで済んでいるかを確認し、Claudeが実行できる段階は実行し、Apple ID認証や審査提出の承認が要る段階はユーザーのターミナルに引き継ぎ、失敗したら原因を調べて再開する。「リリースして」「App Storeに出したい」「ビルドして審査に出して」「fastlaneを実行して」「リリースの続きから」と言われた時、バージョンを上げて出し直す時に使う。"
---

# Releasing To App Store

`fastlane release` を、Claude が「現在地の確認 → 実行できる段階の実行 → 人の操作が要る所での引き継ぎ → 失敗の切り分け」で進める。段階の判定・成功記録・入力ルール検査は `scripts/release`（と `fastlane/Fastfile`）が持っているので、ここでは再実装せず、その出力に従う。

## 大前提

- **審査提出は Claude が実行しない。** 提出はやり直しがきかず、Apple に対する外向きの操作であり、Fastfile も提出直前の内容表示と承認をユーザーに求める設計になっている。Claude のシェルは対話入力ができないため、承認を代行することもできない。提出の直前まで整え、ユーザーに実行してもらう。
- **秘密を読まない・出力しない。** `store/settings.local.json`、`store/review_contact.local.json`（電話番号を含む）、Keychain の中身は開かない。要件で「リポジトリ内から秘密が見つからない」ことが求められているため。設定の過不足は `status` の出力だけで判断する。
- **`build/release_state.json` を手で編集しない。** 入力ファイルのハッシュで成功記録が自動的に無効になる仕組みなので、手で書き換えると古いビルドを新しいものとして扱ってしまう。やり直したい時は、コードを直すか、ユーザーに `fastlane <段階>` を再実行してもらう。

## 進め方

### 1. バージョンを決める

ユーザーが指定していればそれを使う。無ければ `project.yml` の `MARKETING_VERSION` を提示し、この値でよいか確認する。以降の `<version>` はこれ。

### 2. 現在地を確認する

```bash
python3 -m scripts.release.cli status <version>
```

出力（JSON）の読み方:

- `missing_settings` が空でない → 入力すべき場所が書いてあるので、ユーザーに伝えて止まる（値は聞き出さない。ユーザーが自分でファイルに入力する）
- `done` / `pending` / `next_stage` → 済んだ段階と次にやる段階。バージョンが記録と違えば全段階が未実施になる
- `login_guidance` が null でない → Apple ID のセッションが無い/古いので、認証が要る段階（`interactive_stages`）で 2FA コードの入力が求められる

全段階が済んでいる（`next_stage` が null）なら、提出済みなので何もせずそう伝える。

### 3. 提出前の検査をする

```bash
fastlane validate
```

ストア情報の文字数超過、アイコン・審査連絡先・URL の未入力を、ビルドの前に検出する。長いビルドを回した後で提出前に止まるのを避けるため、最初に一度実行する。問題があれば内容をそのままユーザーに伝えて止まる。

### 4. Claude が実行できる段階を実行する

`next_stage` が `test` または `screenshots` のとき（認証が要らない段階）は、Claude が実行する。時間がかかるので `timeout` を最大にするか、バックグラウンドで実行する。

```bash
fastlane <段階> version:<version>
```

成功したら手順2の `status` を再実行して現在地を更新する。失敗したら `references/failure-handling.md` を読んで切り分ける。

### 5. 人の操作が要る段階はユーザーに渡す

`next_stage` が `build` / `upload` / `metadata` / `submit` のとき、または `login_guidance` があるときは、Claude は実行せず、ユーザー自身のターミナル（対話入力ができる場所）で実行してもらう。

- `build` はテスト済みが前提。`test` が済んでいなければ先に手順4へ戻る
- 2FA コード・Apple ID パスワードの入力、提出の承認は、ユーザー本人にしかできない
- 渡すコマンドは残りの段階を一括で進められる `fastlane release version:<version>` にする（成功済みの段階は自動でスキップされ、失敗した段階から再開する）。段階を分けて確認しながら進めたい意向があれば `fastlane <段階> version:<version>`
- 渡す時は、これから何が起きるか（例:「ビルド番号は App Store Connect の最新+1で自動採番」「submit の直前に内容が表示され、承認するまで提出されない」）を1〜2行添える

ユーザーが実行し終えたと言ったら、手順2から繰り返して現在地を確認する。出力にエラーが貼られたら `references/failure-handling.md` へ。

### 6. コードを変更した場合

テスト失敗の修正などでソースを変えると、`test` 以降の成功記録は自動的に無効になり、次の実行で `test` からやり直しになる。これは仕様なので、ユーザーに「変更したのでテストからやり直しになる」と一言伝える。

## 完了の報告

`status` の `next_stage` が null になり、ユーザーが `submit` の成功を確認できたら、次を伝えて終える。

- 提出したバージョンとビルド番号
- App Store Connect のステータスが「審査待ち」になっていること
- 公開は自動ではなく手動リリースであること（`store/settings.json` の `release_method`）

## 参照ファイル

- `references/failure-handling.md` — 段階が失敗した時に読む。エラーの種類ごとの原因と、Claude が直せるものとユーザーに頼むものの切り分け
