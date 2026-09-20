import Foundation
import SwiftData

/// Mirrors `Budgets\Edit`, `Budgets\CategoryEdit`,
/// `GetMonthlyBudgetUseCase`, `SaveMonthlyBudgetUseCase`,
/// `GetCategoryBudgetEditDataUseCase`, `SaveCategoryBudgetUseCase`,
/// `BudgetComparisonService`, and `CategoryBudgetComparisonService` from the
/// Laravel app.
enum BudgetService {

    // MARK: Whole-month budget

    static func monthlyBudgetAmount(for month: TargetMonth, context: ModelContext) -> Int? {
        fetchMonthlyBudget(for: month, context: context)?.amount
    }

    /// Upserts the whole-month budget for `month` (one per month, matching
    /// the Laravel `updateOrCreate` keyed on `(user_id, target_month)`).
    static func saveMonthlyBudget(month: TargetMonth, amount: Int, context: ModelContext) throws {
        _ = try Money(amount)
        if let existing = fetchMonthlyBudget(for: month, context: context) {
            existing.amount = amount
        } else {
            context.insert(MonthlyBudget(targetMonth: month.value, amount: amount))
        }
        try context.save()
    }

    private static func fetchMonthlyBudget(for month: TargetMonth, context: ModelContext) -> MonthlyBudget? {
        let monthValue = month.value
        let descriptor = FetchDescriptor<MonthlyBudget>(predicate: #Predicate { $0.targetMonth == monthValue })
        return try? context.fetch(descriptor).first
    }

    /// Compares the month's budget against actual expense spending.
    /// Views pass their `@Query` result as `monthlyBudgets` so SwiftUI redraws when a budget is saved.
    static func monthlyBudgetStatus(for month: TargetMonth, expenseTotal: Money, monthlyBudgets: [MonthlyBudget]) -> BudgetStatus {
        let monthValue = month.value
        let amount = monthlyBudgets.first { $0.targetMonth == monthValue }?.amount ?? 0
        return BudgetStatus(budgetAmount: Money(clamping: amount), spentAmount: expenseTotal)
    }

    // MARK: Per-category budgets

    /// categoryId -> budgeted amount for `month` (only categories with a
    /// budget set are included), for prefilling the edit form.
    static func categoryBudgetAmounts(for month: TargetMonth, context: ModelContext) -> [PersistentIdentifier: Int] {
        categoryBudgetAmounts(for: month, categoryBudgets: fetchCategoryBudgets(for: month, context: context))
    }

    /// Same, from already-fetched budgets (any month; other months are ignored).
    static func categoryBudgetAmounts(for month: TargetMonth, categoryBudgets: [CategoryBudget]) -> [PersistentIdentifier: Int] {
        let monthValue = month.value
        var result: [PersistentIdentifier: Int] = [:]
        for budget in categoryBudgets where budget.targetMonth == monthValue {
            if let categoryId = budget.category?.persistentModelID {
                result[categoryId] = budget.amount
            }
        }
        return result
    }

    /// Upserts a single category's budget for `month`. Blank/omitted
    /// entries are simply not called with this, matching the Laravel
    /// behavior of skipping blank fields on save (never clearing an
    /// existing value).
    static func saveCategoryBudget(category: Category, month: TargetMonth, amount: Int, context: ModelContext) throws {
        _ = try Money(amount)
        let monthValue = month.value
        let categoryId = category.persistentModelID
        let descriptor = FetchDescriptor<CategoryBudget>(
            predicate: #Predicate<CategoryBudget> { $0.targetMonth == monthValue }
        )
        let existing = (try? context.fetch(descriptor))?.first { $0.category?.persistentModelID == categoryId }

        if let existing {
            existing.amount = amount
        } else {
            context.insert(CategoryBudget(category: category, targetMonth: month.value, amount: amount))
        }
        try context.save()
    }

    private static func fetchCategoryBudgets(for month: TargetMonth, context: ModelContext) -> [CategoryBudget] {
        let monthValue = month.value
        let descriptor = FetchDescriptor<CategoryBudget>(predicate: #Predicate { $0.targetMonth == monthValue })
        return (try? context.fetch(descriptor)) ?? []
    }

    struct CategoryComparison: Identifiable {
        let category: Category
        let status: BudgetStatus
        var id: PersistentIdentifier { category.persistentModelID }
    }

    /// For every category, spent-vs-budgeted for `month`. Always lists all
    /// categories, even ones with no spending or no budget set (matching
    /// `CategoryBudgetComparisonService`).
    static func categoryComparisons(for month: TargetMonth, context: ModelContext) -> [CategoryComparison] {
        categoryComparisons(
            for: month,
            categories: CategoryService.fetchAll(context: context),
            categoryBudgets: (try? context.fetch(FetchDescriptor<CategoryBudget>())) ?? [],
            allTransactions: TransactionService.fetchAll(context: context)
        )
    }

    /// Views pass their `@Query` results so SwiftUI redraws when budgets or transactions change.
    static func categoryComparisons(
        for month: TargetMonth,
        categories: [Category],
        categoryBudgets: [CategoryBudget],
        allTransactions: [Transaction]
    ) -> [CategoryComparison] {
        let budgetsByCategory = categoryBudgetAmounts(for: month, categoryBudgets: categoryBudgets)
        let transactions = TransactionService.filter(allTransactions, for: month)

        var spentByCategory: [PersistentIdentifier: Int] = [:]
        for transaction in transactions where transaction.type == .expense {
            guard let categoryId = transaction.category?.persistentModelID else { continue }
            spentByCategory[categoryId, default: 0] += transaction.amount
        }

        return categories.map { category in
            let spent = Money(clamping: spentByCategory[category.persistentModelID] ?? 0)
            let budget = Money(clamping: budgetsByCategory[category.persistentModelID] ?? 0)
            return CategoryComparison(category: category, status: BudgetStatus(budgetAmount: budget, spentAmount: spent))
        }
    }
}
