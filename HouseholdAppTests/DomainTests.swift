import XCTest
@testable import HouseholdApp

final class MoneyTests: XCTestCase {
    func testRejectsNegativeAmount() {
        XCTAssertThrowsError(try Money(-1))
    }

    func testAddAndSubtract() throws {
        let a = try Money(1000)
        let b = try Money(300)
        XCTAssertEqual(a.add(b).amount, 1300)
        XCTAssertEqual(try a.subtract(b).amount, 700)
    }

    func testSubtractBelowZeroThrows() throws {
        let a = try Money(100)
        let b = try Money(300)
        XCTAssertThrowsError(try a.subtract(b))
    }

    func testDifferenceCanBeNegative() throws {
        let a = try Money(100)
        let b = try Money(300)
        XCTAssertEqual(a.difference(b), -200)
    }

    func testIsGreaterThan() throws {
        XCTAssertTrue(try Money(500).isGreaterThan(Money(499)))
        XCTAssertFalse(try Money(500).isGreaterThan(Money(500)))
    }
}

final class TargetMonthTests: XCTestCase {
    func testValidFormatParses() throws {
        let month = try TargetMonth("2026-03")
        XCTAssertEqual(month.value, "2026-03")
    }

    func testInvalidFormatThrows() {
        XCTAssertThrowsError(try TargetMonth("2026/03"))
        XCTAssertThrowsError(try TargetMonth("26-03"))
        XCTAssertThrowsError(try TargetMonth("not-a-month"))
    }

    func testDateIntervalSpansWholeMonth() throws {
        let month = try TargetMonth("2026-02")
        let calendar = Calendar(identifier: .gregorian)
        let components = calendar.dateComponents([.year, .month, .day], from: month.dateInterval.start)
        XCTAssertEqual(components.year, 2026)
        XCTAssertEqual(components.month, 2)
        XCTAssertEqual(components.day, 1)

        let nextMonthComponents = calendar.dateComponents([.year, .month, .day], from: month.dateInterval.end)
        XCTAssertEqual(nextMonthComponents.year, 2026)
        XCTAssertEqual(nextMonthComponents.month, 3)
        XCTAssertEqual(nextMonthComponents.day, 1)
    }
}

final class BudgetStatusTests: XCTestCase {
    func testNotExceededWhenEqual() throws {
        let status = BudgetStatus(budgetAmount: try Money(1000), spentAmount: try Money(1000))
        XCTAssertFalse(status.isExceeded)
        XCTAssertEqual(status.remainingAmount, 0)
    }

    func testExceededWhenSpentIsGreater() throws {
        let status = BudgetStatus(budgetAmount: try Money(1000), spentAmount: try Money(1500))
        XCTAssertTrue(status.isExceeded)
        XCTAssertEqual(status.remainingAmount, -500)
    }
}
