## 家計簿App (iOS)

[household-app](../household-app)（Laravel + Livewire 版）を Swift / SwiftUI で
iOS ネイティブアプリとして再実装したものです。元アプリと同じドメインモデル・
業務ロジックをレイヤー分離した形で移植しています。

⸻

### 概要

日々の収支を記録し、月単位での集計や予算管理を行うシンプルな家計簿アプリです。
サーバーを持たない端末内完結型（ローカルストレージのみ）のシングルユーザー
アプリとして実装しています。

⸻

### 機能

- 収支（Transaction）の登録・一覧表示
- 月別収支の集計（収入合計・支出合計・収支差額）
- 月予算（MonthlyBudget）の設定
- カテゴリ別予算（CategoryBudget）の設定
- 予算と実績の比較表示（月全体・カテゴリ別）
- カテゴリ別支出の内訳（構成比バー付き）

⸻

### 工夫した点

Claude Code（AI エージェント）と fastlane を使い、要件定義からリリースまでを進められるようにしました。

#### 1. 開発工程を Claude Code のスキルにした

要件定義 → 実装 → レビュー → リリースの各工程を、[.claude/skills/](.claude/skills/) にスキルとして用意しました。
前の工程の成果物（`requirements.md`）を次の工程が受け取るので、工程をまたいでも要件がぶれません。

- **要件定義（defining-requirements）**：AI がプロダクトマネージャー役になり、推奨案付きの選択式の質問を1〜3問ずつ出します。
  決まったことはその場で要件書に書き込み、未決事項が残っている間は実装に進めません。
- **実装（implementing-requirements）**：要件に番号付きのチェックリストを作り、どの変更がどの要件のためかを追えるようにしました。
  実装の抜けと、要件にない作りすぎを防ぐためです。
- **レビュー（reviewing-changes）**：コードを書いた AI 自身は見落としやすいため、観点ごとに別のサブエージェントにレビューさせます。
  指摘だけを返し、直すかどうかは人が決めます。

#### 2. DDD とビルドの速さを、AI に設計基準として守らせる

AI に任せるとコードの置き場所や書き方がばらつくので、設計基準を文書にして、実装とレビューのスキルから必ず参照させています。

- **DDD の設計思想**：[docs/development/ddd-principles.md](docs/development/ddd-principles.md) に、層ごとに置くもの・置かないもの、依存の向き、要件を層に振り分ける基準を定めました。
  実装のスキルはこの基準で置き場所を決め、新しい用語が出たら domain-modeling スキルで用語を確定させてから実装します。
  Aggregate や Repository などは導入する条件を決めておき、AI が先回りして設計を重くしないようにしています。
- **Swift のビルドの速さ**：[docs/development/swift-compile-time.md](docs/development/swift-compile-time.md) に、型推論が重くなる式の分割、View の切り出し、アクセス制御などの規約をまとめました。
  実装のスキルは、Swift のコードを変えるたびに、関数や式ごとのコンパイル時間をスクリプトで計測します。
  しきい値を超えた箇所は遅い順に一覧になり、AI が規約に沿って直してから再計測します。
- **レビューでも機械的に確かめる**：レビューのスキルは、Domain 層が SwiftUI や SwiftData を import していないかなど、依存の向きの違反をスクリプトで検出します。
  そのうえで、DDD とコンパイル時間の基準を担当するサブエージェントが、機械では見つけられない違反を読んで指摘します。

#### 3. AI の出力がぶれないスキル設計

- 要件書の作成・追記、チェックリストの生成、レビュー対象の抽出、ビルド時間の計測など、決まった処理は Python スクリプトに任せました。
  AI に毎回手順を考えさせると、結果が実行ごとに変わるためです。スクリプトは pytest でテストしています。
- `SKILL.md` は短く保ち、詳細な手順は `references/`、サブエージェントへの指示は `agents/` に分けました。
- スキルを作る・見直すためのスキル（creating-agent-skills）と、指示文を Anthropic の最新のプロンプト設計ガイドと照らし合わせるスキル（auditing-prompt-docs）を用意しました。
  モデルが更新されても、スキルの品質を保てます。

#### 4. AI に任せる範囲と、人が決める範囲を分けた

- 審査提出は取り消せない操作なので、AI には実行させません。提出の直前まで AI が整え、承認と実行は人が行います。
- 2 段階認証のコード入力など人の操作が必要な段階では、AI がユーザーのターミナルに作業を引き継ぎます。
- Apple ID の設定・審査連絡先・Keychain の中身は AI に読ませません。足りない設定は、スクリプトの出力だけで判断させます。
- テストが失敗したら AI が原因を調べて直します。ただし、テストを緩めたり消したりして通すことは禁止しています。

#### 5. mobile-mcp で、AI がシミュレータを操作して動作確認する

- [CLAUDE.md](CLAUDE.md) に「機能を実装したら、シミュレータで動作確認してから完了と報告する」というルールを定めました。
  ユニットテストだけでは分からない画面の動きまで、AI が自分で確かめてから完了を報告します。
- 確認手順は機能ごとに [scenarios/](scenarios/) の Markdown にまとめました。AI が [mobile-mcp](https://github.com/mobile-next/mobile-mcp) で画面要素を読み取り、タップや入力をして、期待結果ごとに合否を判定します。
- シミュレータの起動、アプリのビルド、前提データの準備は、起動スクリプトにまとめました。
  mobile-mcp の起動ツールでは起動引数を渡せないため、「空の初期状態」と「サンプルデータあり」をスクリプト側で再現しています。
- 画面部品には表示文言に依存しない識別子を付け、文言を変えても手順が壊れないようにしました。
- mobile-mcp で操作するときの注意点も、シナリオの手引きに残しています。数字キーパッドが入力欄を隠す、要素の参照が取り直すたびに変わる、などです。
- 失敗したらスクリーンショットを保存して報告し、コードもシナリオも勝手には書き換えません。

#### 6. fastlane で、テストから審査提出までを 1 コマンドにした

```sh
fastlane release version:1.0.0
```

テスト → ビルド → TestFlight アップロード → スクリーンショット → ストア情報反映 → 審査提出を、この 1 コマンドで順に実行します。

- **途中から再開できる**：段階ごとに成功を記録し、失敗した段階から再開します。入力ファイルの内容が変わった段階と、それに依存する段階だけをやり直します。
- **送信前に検査する**：ストア文言の文字数上限、アイコンの形式（1024×1024・透過なしの PNG）、審査連絡先、URL を、App Store Connect に送る前に検査します。
- **手作業を残さない**：ビルド番号の採番、スクリーンショットの撮影、価格・公開地域の設定、App のプライバシーの回答までをコードにしました。
  スクリーンショットはサンプルデータ入りでアプリを起動して自動で撮影します。この起動の仕組みは、AI の動作確認と共通です。
- **秘密情報をリポジトリに置かない**：パスワードは Keychain、個人の設定は Git 管理外のファイルに置きました。電話番号を含む審査連絡先は、送信に使った直後に一時ファイルを削除します。
- **fastlane のレーンを薄く保つ**：Fastfile は fastlane の呼び出しと段階の順序だけを持ちます。判定・検査・状態管理は Python（[scripts/release/](scripts/release/)）に分け、pytest でテストしています。

#### 7. fastlane の実行も AI に任せられる

リリース用のスキル（releasing-to-app-store）を使うと、AI がリリースの現在地を確認し、実行できる段階を進めます。
失敗したら、段階ごとにまとめた切り分け手順に沿って原因を調べ、直してから再開します。
段階の判定や検査はスクリプト側に任せ、スキルで同じ処理を作り直さないようにしました。

⸻

### 技術スタック

- Swift 5 / SwiftUI
- SwiftData（端末内永続化）
- XCTest（ユニットテスト）
- [XcodeGen](https://github.com/yonaskolb/XcodeGen)（`project.yml` から `.xcodeproj` を生成）

⸻

### アーキテクチャ

Laravel 版の「Livewire → UseCase → Repository → Eloquent」という責務分離を、
iOS では以下のように対応させています。

| Laravel 版 | iOS 版 | 役割 |
|---|---|---|
| Livewire Component | `Views/` (SwiftUI View) | 入力受付・画面表示 |
| UseCase | `Services/` (enum の static メソッド) | ビジネスロジックの実行 |
| Domain (ValueObject) | `Domain/` | 不正な状態を型で防ぐ値オブジェクト |
| Repository / Eloquent Model | `Models/` (SwiftData `@Model`) | 永続化 |

```
HouseholdApp/
├── App/                 アプリ起動・ModelContainer 初期化
├── Domain/               Money / TargetMonth / BudgetStatus / TransactionType
├── Models/                SwiftData モデル（Category / Transaction / MonthlyBudget / CategoryBudget）
├── Services/              TransactionService / BudgetService / ReportService / CategoryService / SeedDataService
├── Views/
│   ├── Reports/            月別集計（ホーム画面）
│   ├── Transactions/       収支登録・一覧
│   ├── Budgets/            月予算・カテゴリ別予算の設定
│   └── Components/         再利用可能な UI 部品
└── Resources/              Assets.xcassets
HouseholdAppTests/          Domain / Service のユニットテスト
```

#### Value Object（`Domain/`）

Laravel 版と同じ不変条件をそのまま Swift の値型で表現しています。

- `Money` — 0 以上の整数（円）。負の金額は生成不可、減算結果が負になる場合は例外
- `TargetMonth` — `"yyyy-MM"` 形式の対象月。不正な形式は生成不可
- `BudgetStatus` — 予算と実績の比較（残額・超過判定は「支出 > 予算」の場合のみ超過）
- `TransactionType` — 収入 / 支出

⸻

### Laravel 版との差分

元の Laravel アプリは家計簿機能自体に認証がかかっておらず、実質シングルユーザー
（`userId = 1` 固定）で動作していました。iOS 版ではこれを踏まえ、以下の方針で
移植しています。

- **認証機能は実装していません。** ログイン画面や 2 段階認証（Fortify 相当）は
  再現せず、端末 = 1 ユーザーとして家計簿機能のみを実装しています。
- **バックエンド API は使用していません。** サーバーレンダリングだった Laravel
  版に対し、iOS 版はネットワーク通信を行わず SwiftData で端末内にのみデータを
  保存します。他端末との同期はありません。
- カテゴリの追加・編集・削除 UI は元アプリ同様に未実装です（起動時に既定の6
  カテゴリをシードするのみ）。
- 取引・予算の編集・削除 UI も元アプリ同様に未実装です（新規登録のみ）。

⸻

### セットアップ

```sh
brew install xcodegen   # 未導入の場合
cd household-app-ios
xcodegen generate       # project.yml から HouseholdApp.xcodeproj を生成
open HouseholdApp.xcodeproj
```

Xcode で `HouseholdApp` スキームを選択し、iOS シミュレータで実行してください。

`HouseholdApp.xcodeproj` は `project.yml` から生成される成果物のため Git 管理
対象外（`.gitignore`）にしています。プロジェクト構成を変更した場合は
`project.yml` を編集し、`xcodegen generate` を再実行してください。

#### テスト

```sh
xcodebuild -project HouseholdApp.xcodeproj -scheme HouseholdApp \
  -destination 'platform=iOS Simulator,name=iPhone 16' test
```

または Xcode 上で `⌘U`。

⸻

### リリース（ビルド〜App Store 審査提出）

fastlane と `scripts/release/` で、テスト・ビルド・アップロード・ストア情報反映・審査提出を
ローカルの Mac から実行します。CI からの実行は対象外です。

#### 事前準備（初回のみ）

1. `brew install fastlane xcodegen`、Xcode に Apple ID でサインイン（自動署名用）
2. `store/settings.local.example.json` を `store/settings.local.json` にコピーして
   `apple_id` と `team_id` を入力（Git 管理外。`store/settings.json` の同名キーを上書きします）
3. `fastlane setup_credentials` で Apple ID のパスワードとアプリ用パスワード
   （appleid.apple.com で発行）を Keychain に登録（リポジトリには保存されません）
4. アプリアイコン（1024x1024 の PNG、透過なし）を `AppIcon.appiconset` に置き、
   `Contents.json` の `images` に `"filename"` を追記
5. `store/review_contact.example.json` を `store/review_contact.local.json` にコピーして
   審査連絡先を入力（Git 管理外）
6. `store/metadata/ja/privacy_url.txt` と `support_url.txt` に URL を入力
7. `store/name_candidates.txt` からアプリ名を選び、`fastlane create_app`
   （名前が重複したら `fastlane create_app candidate:2` のように次の候補で再試行）

#### 実行

```sh
fastlane release version:1.0.0   # 全段階を順に実行。成功済みの段階は飛ばして再開
fastlane test | build | upload | screenshots | metadata | submit   # 単独実行
fastlane validate                # 入力ルールと審査提出の前提だけ検査
```

- 段階の順序: test → build → upload → screenshots → metadata → submit。テストが失敗したらビルド以降は実行しません
- ビルド番号は App Store Connect の最新番号 + 1 を自動採番します。`version:` は表示バージョンです
- 審査提出の直前に内容を表示し、承認するまで提出しません。審査通過後は手動リリースです
- 段階の成功記録は `build/release_state.json`（Git 管理外）。入力ファイルが変わった段階はやり直します
- セッション Cookie が有効な間は認証を求めません。期限切れのときだけ 2FA コードをターミナルに入力します

#### ストア情報

`store/metadata/ja/` のテキストが App Store Connect の日本語ページに反映されます。
文字数の上限（名前・サブタイトル 30、キーワード 100、説明文 4000）を超えると反映せずに止まります。
審査情報の既定値（カテゴリ・年齢制限・暗号化・価格など）は `store/settings.json` にあります。
「App のプライバシー」は `store/app_privacy_details.json`（現在は「データ収集なし」）を metadata 段階で回答・公開します。
価格（無料）と公開地域（日本のみ）は metadata 段階で自動設定します（失敗時は提出前の表示で手作業を促します）。
アプリは iPhone 専用（`TARGETED_DEVICE_FAMILY: "1"`）で、スクリーンショットは iPhone 6.9 インチのみです。
スクリーンショットは `fastlane screenshots` がシミュレータで撮影し `store/screenshots/ja/` に置きます
（`-ScreenshotSampleData` 起動引数でサンプルデータ入りのインメモリ状態で起動します）。


#### スクリプトのテスト

```sh
python3 -m pytest scripts/release
```
