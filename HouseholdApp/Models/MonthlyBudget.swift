import Foundation
import SwiftData

/// Mirrors the Laravel `monthly_budgets` table: one whole-month budget per
/// `targetMonth` ("yyyy-MM"). Upserted by `BudgetService.saveMonthlyBudget`,
/// which enforces the one-per-month rule in code (as the Laravel app does).
@Model
final class MonthlyBudget {
    var id: UUID
    /// "yyyy-MM"
    var targetMonth: String
    var amount: Int
    var createdAt: Date

    init(targetMonth: String, amount: Int) {
        self.id = UUID()
        self.targetMonth = targetMonth
        self.amount = amount
        self.createdAt = Date()
    }
}
