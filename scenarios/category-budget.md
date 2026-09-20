# カテゴリ別予算の設定

前提: 空の初期状態

数字キーパッドには閉じるボタンが無く、開いている間はタブバーが隠れる。入力後の画面移動は「戻る」「保存」で行う。

## 手順

1. 画面下のタブ「予算設定」をタップし、`budgetMenu.categoryBudgetLink` をタップする
   - 期待: 「カテゴリ別予算設定」画面が開く
   - 期待: 家賃・給料・娯楽・交通費・光熱費・食費の6つの入力欄（`categoryBudgetEdit.amountField.<カテゴリ名>`）があり、すべて空
2. `categoryBudgetEdit.amountField.食費` に `50000`、`categoryBudgetEdit.amountField.交通費` に `15000` を入力する（他は空のまま）
   - 期待: 2つの欄にそれぞれ入力した金額が入る
3. `categoryBudgetEdit.saveButton` をタップする
   - 期待: `categoryBudgetEdit.savedMessage` に「カテゴリ別予算を保存しました。」が表示される
   - 期待: `categoryBudgetEdit.errorMessage` は表示されない
4. ナビゲーションバー左上の戻るボタンで予算設定に戻り、もう一度 `budgetMenu.categoryBudgetLink` をタップする
   - 期待: 食費の欄が「50000」、交通費の欄が「15000」で、他の4つは空のまま
5. 戻るボタンで予算設定に戻り、画面下のタブ「月別集計」をタップして「カテゴリ別予算比較」までスクロールする
   - 期待: 食費が「支出 0円 / 予算 50,000円」、交通費が「支出 0円 / 予算 15,000円」
   - 期待: 他のカテゴリは「支出 0円 / 予算 0円」
