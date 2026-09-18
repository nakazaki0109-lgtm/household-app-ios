import Foundation

/// Mirrors `App\Domain\Budget\TargetMonth` from the Laravel app: a "Y-m"
/// string such as "2026-03" used to key monthly budgets and reports.
struct TargetMonth: Equatable, Codable, Hashable {
    enum Error: Swift.Error, LocalizedError {
        case invalidFormat

        var errorDescription: String? {
            "対象月は yyyy-MM 形式である必要があります。"
        }
    }

    /// "yyyy-MM"
    let value: String

    init(_ value: String) throws {
        guard value.range(of: #"^\d{4}-\d{2}$"#, options: .regularExpression) != nil else {
            throw Error.invalidFormat
        }
        self.value = value
    }

    /// Non-throwing convenience for building from a `Date`.
    init(date: Date, calendar: Calendar = .current) {
        let formatter = TargetMonth.formatter
        self.value = formatter.string(from: date)
    }

    static func current(calendar: Calendar = .current) -> TargetMonth {
        TargetMonth(date: Date(), calendar: calendar)
    }

    /// First day of the month, used as the persisted date key (mirrors the
    /// Laravel side storing `target_month` as `Y-m-01`).
    var monthDate: Date {
        TargetMonth.formatter.date(from: value) ?? Date()
    }

    var startDate: Date { monthDate }

    var endDate: Date {
        let calendar = Calendar.current
        let range = calendar.range(of: .day, in: .month, for: monthDate) ?? 1..<2
        return calendar.date(byAdding: .day, value: range.count - 1, to: monthDate) ?? monthDate
    }

    /// Convenience half-open range `[startOfMonth, startOfNextMonth)` for
    /// date-range queries.
    var dateInterval: DateInterval {
        let calendar = Calendar.current
        let end = calendar.date(byAdding: .month, value: 1, to: startDate) ?? endDate
        return DateInterval(start: startDate, end: end)
    }

    private static let formatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = .current
        formatter.dateFormat = "yyyy-MM"
        return formatter
    }()
}
