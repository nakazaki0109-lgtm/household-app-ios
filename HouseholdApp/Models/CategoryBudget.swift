import Foundation
import SwiftData

/// Mirrors the Laravel `category_budgets` table: one budget per
/// (category, targetMonth), enforced as a uniqueness rule by
/// `BudgetService.saveCategoryBudget` (upsert), matching the Laravel
/// DB-level unique constraint on `(user_id, category_id, target_month)`.
@Model
final class CategoryBudget {
    var id: UUID
    /// "yyyy-MM"
    var targetMonth: String
    var amount: Int
    var createdAt: Date

    var category: Category?

    init(category: Category, targetMonth: String, amount: Int) {
        self.id = UUID()
        self.category = category
        self.targetMonth = targetMonth
        self.amount = amount
        self.createdAt = Date()
    }
}
