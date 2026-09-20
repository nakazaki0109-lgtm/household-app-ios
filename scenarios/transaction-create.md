# 収支の登録

前提: 空の初期状態

## 手順

1. 月別集計タブで `summary.addTransactionButton` をタップする
   - 期待: 「収支登録」画面が開き、種別は「支出」が選択されている
   - 期待: 金額・メモが空で、カテゴリは「選択してください」
2. 金額を空のまま `transactionCreate.saveButton` をタップする
   - 期待: `transactionCreate.errorMessage` に「金額は数値で入力してください。」が表示される
   - 期待: 画面は閉じない
3. `transactionCreate.categoryPicker` をタップして「食費」を選ぶ
   - 期待: カテゴリが「食費」になる
4. `transactionCreate.memoField` をタップして `ランチ` を入力する
   - 期待: メモが「ランチ」になる
5. `transactionCreate.amountField` をタップして `0` を入力し、`transactionCreate.saveButton` をタップする
   - 期待: `transactionCreate.errorMessage` に「金額は1以上を入力してください。」が表示される
   - 期待: 画面は閉じない
6. 続けて `transactionCreate.amountField` に `1500` を入力する（欄は `01500` になるが、金額は1500として扱われる）
   - 期待: `transactionCreate.amountField` の値が「01500」になる
7. `transactionCreate.saveButton` をタップする
   - 期待: 収支登録画面が閉じ、月別集計に戻る
8. 月別集計の合計を見る
   - 期待: 収入合計「0円」、支出合計「1,500円」、収支差額「-1,500円」
   - 期待: 「カテゴリ別支出」に食費 1,500円（100.0%）が表示される
   - 期待: 「この月の収支」に、今日の日付・支出・食費・「ランチ」・1,500円の行が1件だけ表示される
9. 画面下のタブ「収支一覧」をタップする
   - 期待: 手順8と同じ1件が表示され、「まだ収支データがありません。」は表示されない
