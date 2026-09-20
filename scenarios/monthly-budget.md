# 月予算の設定

前提: 空の初期状態

数字キーパッドには閉じるボタンが無く、開いている間はタブバーが隠れる。入力後の画面移動は「戻る」「保存」で行う。

## 手順

1. 月別集計タブで `summary.monthlyBudgetLink` をタップする
   - 期待: 「月予算設定」画面が開き、当月が表示されている
   - 期待: `monthlyBudgetEdit.amountField` が空
2. `monthlyBudgetEdit.amountField` に `200000` を入力し、`monthlyBudgetEdit.saveButton` をタップする
   - 期待: `monthlyBudgetEdit.savedMessage` に「月予算を保存しました。」が表示される
   - 期待: `monthlyBudgetEdit.errorMessage` は表示されない
3. ナビゲーションバー左上の戻るボタンで月別集計に戻り、もう一度 `summary.monthlyBudgetLink` をタップする
   - 期待: `monthlyBudgetEdit.amountField` の値が「200000」になっている
4. 戻るボタンで月別集計に戻る
   - 期待: 今月の予算が「200,000円」、残額が「200,000円」、予算判定が「予算内」
