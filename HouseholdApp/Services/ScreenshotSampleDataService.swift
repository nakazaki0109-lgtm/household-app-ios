import Foundation
import SwiftData

/// App Store 用スクリーンショットに写すサンプルデータを投入する。
/// 端末の実データを汚さないよう、呼び出し側はインメモリのコンテナだけに使う。
enum ScreenshotSampleDataService {
    private struct SampleTransaction {
        let type: TransactionType
        let categoryName: String
        let amount: Int
        let day: Int
        let memo: String
    }

    private static let monthlyBudgetAmount = 250_000

    private static let categoryBudgets: [String: Int] = [
        "食費": 50_000,
        "交通費": 15_000,
        "家賃": 85_000,
        "光熱費": 20_000,
        "娯楽": 20_000
    ]

    private static let transactions: [SampleTransaction] = [
        SampleTransaction(type: .income, categoryName: "給料", amount: 320_000, day: 1, memo: "給与"),
        SampleTransaction(type: .expense, categoryName: "家賃", amount: 85_000, day: 1, memo: "今月の家賃"),
        SampleTransaction(type: .expense, categoryName: "光熱費", amount: 8_400, day: 3, memo: "電気代"),
        SampleTransaction(type: .expense, categoryName: "食費", amount: 3_280, day: 4, memo: "スーパー"),
        SampleTransaction(type: .expense, categoryName: "交通費", amount: 4_500, day: 6, memo: "定期券チャージ"),
        SampleTransaction(type: .expense, categoryName: "食費", amount: 1_200, day: 8, memo: "ランチ"),
        SampleTransaction(type: .expense, categoryName: "娯楽", amount: 1_900, day: 10, memo: "映画"),
        SampleTransaction(type: .expense, categoryName: "食費", amount: 5_640, day: 12, memo: "まとめ買い"),
        SampleTransaction(type: .expense, categoryName: "光熱費", amount: 4_100, day: 14, memo: "ガス代"),
        SampleTransaction(type: .expense, categoryName: "娯楽", amount: 6_800, day: 16, memo: "友人と食事"),
        SampleTransaction(type: .expense, categoryName: "食費", amount: 2_450, day: 18, memo: "カフェ・パン")
    ]

    /// カテゴリは `SeedDataService` が先に投入している前提。見つからない行は飛ばす。
    static func seed(month: TargetMonth, context: ModelContext) throws {
        let categories = CategoryService.fetchAll(context: context)
        var categoriesByName: [String: Category] = [:]
        for category in categories {
            categoriesByName[category.name] = category
        }

        try BudgetService.saveMonthlyBudget(month: month, amount: monthlyBudgetAmount, context: context)

        for (name, amount) in categoryBudgets {
            guard let category = categoriesByName[name] else { continue }
            try BudgetService.saveCategoryBudget(category: category, month: month, amount: amount, context: context)
        }

        for sample in transactions {
            let date = dayDate(sample.day, in: month)
            try TransactionService.save(
                type: sample.type,
                amount: sample.amount,
                transactionDate: date,
                category: categoriesByName[sample.categoryName],
                memo: sample.memo,
                context: context
            )
        }
    }

    private static func dayDate(_ day: Int, in month: TargetMonth) -> Date {
        let offset = day - 1
        return Calendar.current.date(byAdding: .day, value: offset, to: month.startDate) ?? month.startDate
    }
}
