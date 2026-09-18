import Foundation

/// Mirrors `App\Domain\Budget\BudgetStatus` from the Laravel app: compares a
/// budgeted amount against an actual spent amount for a given month.
struct BudgetStatus: Equatable {
    let budgetAmount: Money
    let spentAmount: Money

    /// Budget minus spent; can be negative when overspent.
    var remainingAmount: Int {
        budgetAmount.difference(spentAmount)
    }

    /// Strictly `spent > budget` — equal is not considered exceeded,
    /// matching the Laravel domain rule.
    var isExceeded: Bool {
        spentAmount.isGreaterThan(budgetAmount)
    }
}
