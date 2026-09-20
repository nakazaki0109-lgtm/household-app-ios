import Foundation

/// 操作部品のアクセシビリティ識別子。mobile-mcp の画面要素の一覧から、表示文言に依存せず特定するために使う。
/// 命名は `画面.部品`。新しい画面の操作部品 (ボタン・入力欄・ピッカーなど) にも必ずここへ追加して付ける。
/// タブバーのボタンは SwiftUI から識別子を付けられないので、ラベル (月別集計・収支一覧・予算設定) で特定する。
enum AccessibilityID {
    enum MonthPicker {
        static let previousButton = "monthPicker.previousButton"
        static let nextButton = "monthPicker.nextButton"
    }

    enum Summary {
        static let addTransactionButton = "summary.addTransactionButton"
        static let monthlyBudgetLink = "summary.monthlyBudgetLink"
        static let categoryBudgetLink = "summary.categoryBudgetLink"
    }

    enum TransactionList {
        static let addButton = "transactionList.addButton"
    }

    enum TransactionCreate {
        static let typePicker = "transactionCreate.typePicker"
        static let amountField = "transactionCreate.amountField"
        static let datePicker = "transactionCreate.datePicker"
        static let categoryPicker = "transactionCreate.categoryPicker"
        static let memoField = "transactionCreate.memoField"
        static let cancelButton = "transactionCreate.cancelButton"
        static let saveButton = "transactionCreate.saveButton"
        static let errorMessage = "transactionCreate.errorMessage"
    }

    enum BudgetMenu {
        static let monthlyBudgetLink = "budgetMenu.monthlyBudgetLink"
        static let categoryBudgetLink = "budgetMenu.categoryBudgetLink"
    }

    enum MonthlyBudgetEdit {
        static let amountField = "monthlyBudgetEdit.amountField"
        static let saveButton = "monthlyBudgetEdit.saveButton"
        static let savedMessage = "monthlyBudgetEdit.savedMessage"
        static let errorMessage = "monthlyBudgetEdit.errorMessage"
    }

    enum CategoryBudgetEdit {
        static let saveButton = "categoryBudgetEdit.saveButton"
        static let savedMessage = "categoryBudgetEdit.savedMessage"
        static let errorMessage = "categoryBudgetEdit.errorMessage"

        /// カテゴリごとの予算入力欄。カテゴリ名は既定カテゴリ (食費・交通費 …) をそのまま使う。
        static func amountField(categoryName: String) -> String {
            "categoryBudgetEdit.amountField.\(categoryName)"
        }
    }
}
