import XCTest
import SwiftData
@testable import HouseholdApp

@MainActor
final class ServiceTests: XCTestCase {
    private var container: ModelContainer!
    private var context: ModelContext!

    override func setUpWithError() throws {
        container = try ModelContainer(
            for: Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self,
            configurations: ModelConfiguration(isStoredInMemoryOnly: true)
        )
        context = container.mainContext
    }

    func testTransactionSaveRejectsZeroAmount() {
        XCTAssertThrowsError(
            try TransactionService.save(type: .expense, amount: 0, transactionDate: Date(), category: nil, memo: nil, context: context)
        )
    }

    func testTransactionSaveTrimsBlankMemoToNil() throws {
        let transaction = try TransactionService.save(
            type: .expense, amount: 1000, transactionDate: Date(), category: nil, memo: "   ", context: context
        )
        XCTAssertNil(transaction.memo)
    }

    func testMonthlyBudgetUpsertOverwritesPreviousValue() throws {
        let month = try TargetMonth("2026-03")
        try BudgetService.saveMonthlyBudget(month: month, amount: 50000, context: context)
        try BudgetService.saveMonthlyBudget(month: month, amount: 80000, context: context)

        let all = try context.fetch(FetchDescriptor<MonthlyBudget>())
        XCTAssertEqual(all.count, 1, "saving twice for the same month should upsert, not duplicate")
        XCTAssertEqual(all.first?.amount, 80000)
    }

    func testCategoryBudgetUpsertIsScopedPerMonth() throws {
        let category = Category(name: "食費")
        context.insert(category)

        let march = try TargetMonth("2026-03")
        let april = try TargetMonth("2026-04")
        try BudgetService.saveCategoryBudget(category: category, month: march, amount: 20000, context: context)
        try BudgetService.saveCategoryBudget(category: category, month: april, amount: 25000, context: context)

        let marchAmounts = BudgetService.categoryBudgetAmounts(for: march, context: context)
        let aprilAmounts = BudgetService.categoryBudgetAmounts(for: april, context: context)
        XCTAssertEqual(marchAmounts[category.persistentModelID], 20000)
        XCTAssertEqual(aprilAmounts[category.persistentModelID], 25000)
    }

    func testMonthlySummaryComputesTotalsAndBalance() throws {
        let food = Category(name: "食費")
        context.insert(food)
        let month = try TargetMonth("2026-03")
        let inMonthDate = month.monthDate

        try TransactionService.save(type: .income, amount: 300000, transactionDate: inMonthDate, category: nil, memo: nil, context: context)
        try TransactionService.save(type: .expense, amount: 40000, transactionDate: inMonthDate, category: food, memo: nil, context: context)

        // Outside the target month — must not be included.
        let calendar = Calendar.current
        let nextMonthDate = calendar.date(byAdding: .month, value: 1, to: inMonthDate)!
        try TransactionService.save(type: .expense, amount: 99999, transactionDate: nextMonthDate, category: food, memo: nil, context: context)

        let summary = ReportService.monthlySummary(for: month, context: context)
        XCTAssertEqual(summary.incomeTotal.amount, 300000)
        XCTAssertEqual(summary.expenseTotal.amount, 40000)
        XCTAssertEqual(summary.balance, 260000)
        XCTAssertEqual(summary.categorySummaries.first?.categoryName, "食費")
    }

    func testCategoryComparisonMarksExceededOnlyWhenStrictlyOver() throws {
        let food = Category(name: "食費")
        context.insert(food)
        let month = try TargetMonth("2026-03")
        try BudgetService.saveCategoryBudget(category: food, month: month, amount: 10000, context: context)
        try TransactionService.save(type: .expense, amount: 10000, transactionDate: month.monthDate, category: food, memo: nil, context: context)

        let comparisons = BudgetService.categoryComparisons(for: month, context: context)
        let foodComparison = comparisons.first { $0.category.persistentModelID == food.persistentModelID }
        XCTAssertEqual(foodComparison?.status.isExceeded, false, "spent == budget must not count as exceeded")
    }

    func testSeedDataServiceIsIdempotent() {
        SeedDataService.seedDefaultCategoriesIfNeeded(context: context)
        SeedDataService.seedDefaultCategoriesIfNeeded(context: context)

        let categories = CategoryService.fetchAll(context: context)
        XCTAssertEqual(categories.count, SeedDataService.defaultCategoryNames.count)
    }
}
