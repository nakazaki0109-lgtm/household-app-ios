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
