import XCTest
import SwiftData
@testable import HouseholdApp

final class LaunchOptionsTests: XCTestCase {
    func testDefaultsWhenNoFlags() {
        let options = LaunchOptions(arguments: ["HouseholdApp"])
        XCTAssertFalse(options.usesSampleData)
        XCTAssertEqual(options.initialTab, 0)
    }

    func testSampleDataAndTabFlags() {
        let options = LaunchOptions(arguments: ["HouseholdApp", "-ScreenshotSampleData", "-ScreenshotTab", "2"])
        XCTAssertTrue(options.usesSampleData)
        XCTAssertEqual(options.initialTab, 2)
    }

    func testInvalidTabFallsBackToFirstTab() {
        XCTAssertEqual(LaunchOptions(arguments: ["-ScreenshotTab", "9"]).initialTab, 0)
        XCTAssertEqual(LaunchOptions(arguments: ["-ScreenshotTab", "x"]).initialTab, 0)
        XCTAssertEqual(LaunchOptions(arguments: ["-ScreenshotTab"]).initialTab, 0)
    }
}

@MainActor
final class ScreenshotSampleDataTests: XCTestCase {
    private var container: ModelContainer!
    private var context: ModelContext!

    override func setUpWithError() throws {
        container = try ModelContainer(
            for: Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self,
            configurations: ModelConfiguration(isStoredInMemoryOnly: true)
        )
        context = container.mainContext
        SeedDataService.seedDefaultCategoriesIfNeeded(context: context)
    }

    func testSeedCreatesTransactionsAndBudgetsForTheMonth() throws {
        let month = try TargetMonth("2026-03")
        try ScreenshotSampleDataService.seed(month: month, context: context)

        let transactions = TransactionService.fetch(for: month, context: context)
        XCTAssertEqual(transactions.count, 11)
        XCTAssertEqual(BudgetService.monthlyBudgetAmount(for: month, context: context), 250_000)

        let budgets = try context.fetch(FetchDescriptor<CategoryBudget>())
        XCTAssertEqual(budgets.count, 5)
    }
}
