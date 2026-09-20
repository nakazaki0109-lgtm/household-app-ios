# 失敗の切り分け

段階が失敗したら、まず出力の**最後のエラー行**と、`build/logs/` にログがあればそれ（テストは `build/logs/test.log`）を読む。原因が特定できるまで再実行を繰り返さない（同じ失敗を重ねるだけで、App Store Connect への問い合わせが増える段階もあるため）。

## 目次

- test（ユニットテスト失敗）
- build（署名・ビルド番号）
- upload
- screenshots
- metadata / validate
- submit
- 認証（2FA・Keychain）

## test（ユニットテスト失敗）

- Claude が直せる。失敗したテスト名と原因を読み、コード（またはテストの誤り）を直す。要件の意図とテストのどちらが正しいかが分からないときは、`requirements.md` を確認し、それでも決まらなければユーザーに聞く。テストを通すためだけにテストを緩めたり消したりしない。
- 直したら `fastlane test version:<version>` を再実行する。ソースを変えたので、以降の段階の成功記録は自動で無効になる。

## build（署名・ビルド番号）

- `署名・認証の設定が足りません` → `status` の `missing_settings` の通り、`store/settings.local.json` の `apple_id` / `team_id` の入力が必要。ユーザーの作業。
- `App Store Connect からビルド番号を取得できません` → アプリ枠が未作成の可能性。ユーザーに `fastlane create_app`（README の事前準備7）を案内する。認証切れの場合は下の「認証」。
- 署名/プロビジョニングのエラー → Xcode に Apple ID でサインインしているか、Team ID が正しいかをユーザーに確認してもらう。証明書の作成や失効はユーザーの操作。
- コンパイルエラー → Claude が直せる。ただし `xcodegen generate` 後の `HouseholdApp.xcodeproj` は Git 管理外なので、直す対象は `project.yml` とソース。

## upload

- `ビルド番号 N は App Store Connect に登録済み` → 別のビルドが先に上がっている。`fastlane build` からやり直すと自動で次の番号になる。ユーザーに再実行を頼む。
- `アプリ用パスワードが Keychain にありません` → ユーザーに `fastlane setup_credentials`。パスワードは Claude に渡してもらわない。
- 処理待ちで長時間止まる → App Store Connect 側のビルド処理待ち。数分〜数十分かかることがあるので、中断せず待つようユーザーに伝える。

## screenshots

- シミュレータの起動失敗・タイムアウト → `xcrun simctl list devices` で対象機種（iPhone 6.9 インチ）が存在するか確認する。無ければ Xcode の Runtimes/Devices で追加が必要（ユーザーの作業）。
- 撮影は済んだが画面が空 → `-ScreenshotSampleData` 起動引数のサンプルデータ経路の不具合の可能性。Claude がコードを調べて直せる。

## metadata / validate

- 文字数超過（名前・サブタイトル30、キーワード100、説明文4000）→ `store/metadata/ja/` の該当ファイルを Claude が短くできる。ただし文言はユーザーの意図に関わるので、削る候補を提示して選んでもらう。
- `privacy_url.txt` / `support_url.txt` 未入力 → ユーザーが入力する（要件で手動入力と決まっている）。Claude は URL を推測して書かない。
- アイコン未設定・審査連絡先ファイルなし → 足りない項目と場所が出力されるので、そのままユーザーに伝える。連絡先ファイルの中身は Claude が作らない。
- アプリ名の重複 → `fastlane create_app candidate:2` のように次の候補で再試行（ユーザーが実行）。

## submit

- `アップロードとストア情報反映が済んでいません` → `upload` と `metadata` を先に済ませる。コードやストア情報を変えた後は無効になっている。
- 承認しなかった → 正常終了ではなく「提出していない」状態。何も壊れていない。準備ができたら `fastlane submit version:<version>` を再実行してもらう。

## 認証（2FA・Keychain）

- 2FA コードの入力待ち・パスワード要求 → ユーザーのターミナルで入力してもらう。入力後は同じ段階が続行される。Claude は代行できず、コードやパスワードを聞き出して保持しない。
- セッション Cookie の期限切れ → 上と同じ。約30日で切れる。
- Keychain に Apple ID パスワードがない → 初回入力で保存される。先に登録するなら `fastlane setup_credentials`。
