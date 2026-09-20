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
2. `store/settings.json` の `apple_id` と `team_id` を入力
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
