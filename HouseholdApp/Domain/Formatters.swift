import Foundation

/// Thousands-separated yen formatting, matching the Laravel views'
/// `number_format($amount) . '円'`.
enum YenFormatter {
    private static let numberFormatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        formatter.usesGroupingSeparator = true
        return formatter
    }()

    static func string(_ amount: Int) -> String {
        let formatted = numberFormatter.string(from: NSNumber(value: amount)) ?? "\(amount)"
        return "\(formatted)円"
    }

    static func string(_ money: Money) -> String {
        string(money.amount)
    }

    /// Signed variant for balances/remaining amounts that can go negative.
    static func signedString(_ amount: Int) -> String {
        amount < 0 ? "-\(string(-amount))" : string(amount)
    }
}

extension DateFormatter {
    static let monthInput: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM"
        return formatter
    }()

    static let dateDisplay: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "ja_JP")
        formatter.dateFormat = "yyyy/MM/dd"
        return formatter
    }()
}
