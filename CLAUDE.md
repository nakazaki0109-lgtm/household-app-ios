# household-app-ios

家計簿 iOS アプリ（SwiftUI / SwiftData）。構成とセットアップは README.md を参照。

## 機能開発時の動作確認（mobile-mcp）

機能を実装したら、完了と報告する前に、シミュレータで動作確認する。手順は `scenarios/README.md`。

1. 新機能のシナリオを `scenarios/<機能名>.md` に追加する（画面を変えたときは影響する既存シナリオも直す。既存シナリオの変更はユーザーに確認する）
2. 新機能のシナリオ、続けて既存のシナリオをすべて実行する。シナリオごとの合否の一覧を報告する
3. 失敗したら、`scenarios/README.md` の「失敗したとき」に従い、コードもシナリオも自動で書き換えずに報告する

画面に操作部品（ボタン・入力欄・ピッカーなど）を追加したら、`HouseholdApp/Views/AccessibilityID.swift` に識別子を足して `.accessibilityIdentifier(...)` を付ける。

mobile-mcp は `.mcp.json` で設定済み（Node.js 20 以上と Xcode コマンドラインツールが前提）。実行端末は iPhone 16 シミュレータのみ。
