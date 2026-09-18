import Foundation
import SwiftData

/// Mirrors `Reports\MonthlySummary` and `GetMonthlySummaryUseCase` from the
/// Laravel app.
enum ReportService {
    struct CategorySummary: Identifiable {
        let categoryName: String
        let totalAmount: Money
        var id: String { categoryName }

        /// Percentage of total month expense, rounded to 1 decimal; 0 when
        /// total expense is 0 (matches the Laravel view's divide-by-zero
        /// guard).
        func percentage(ofExpenseTotal expenseTotal: Money) -> Double {
            guard expenseTotal.amount > 0 else { return 0 }
            let raw = Double(totalAmount.amount) / Double(expenseTotal.amount) * 100
            return (raw * 10).rounded() / 10
        }
    }

    struct MonthlySummary {
        let incomeTotal: Money
        let expenseTotal: Money
        /// income - expense; can be negative.
        var balance: Int { incomeTotal.difference(expenseTotal) }
        let categorySummaries: [CategorySummary]
        let transactions: [Transaction]
    }

    static func monthlySummary(for month: TargetMonth, context: ModelContext) -> MonthlySummary {
        let transactions = TransactionService.fetch(for: month, context: context)

        let incomeTotal = transactions.filter { $0.type == .income }.reduce(0) { $0 + $1.amount }
        let expenseTotal = transactions.filter { $0.type == .expense }.reduce(0) { $0 + $1.amount }

        var expenseByCategory: [String: Int] = [:]
        for transaction in transactions where transaction.type == .expense {
            let name = transaction.category?.name ?? "未分類"
            expenseByCategory[name, default: 0] += transaction.amount
        }
        let categorySummaries = expenseByCategory
            .map { CategorySummary(categoryName: $0.key, totalAmount: Money(clamping: $0.value)) }
            .sorted { $0.totalAmount.amount > $1.totalAmount.amount }

        return MonthlySummary(
            incomeTotal: Money(clamping: incomeTotal),
            expenseTotal: Money(clamping: expenseTotal),
            categorySummaries: categorySummaries,
            transactions: transactions
        )
    }
}
