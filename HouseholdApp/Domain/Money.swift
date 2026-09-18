import Foundation

/// Mirrors `App\Domain\Shared\Money` from the Laravel app: a non-negative,
/// whole-yen amount. Construction fails for negative values, matching the
/// PHP value object's `InvalidArgumentException`.
struct Money: Equatable, Comparable, Codable {
    enum Error: Swift.Error, LocalizedError {
        case negativeAmount
        case negativeResult

        var errorDescription: String? {
            switch self {
            case .negativeAmount: return "金額は0以上である必要があります。"
            case .negativeResult: return "計算結果が0未満になります。"
            }
        }
    }

    let amount: Int

    init(_ amount: Int) throws {
        guard amount >= 0 else { throw Error.negativeAmount }
        self.amount = amount
    }

    /// Non-throwing convenience for call sites that already guarantee a
    /// non-negative value (e.g. summed totals).
    init(clamping amount: Int) {
        self.amount = max(0, amount)
    }

    static func zero() -> Money { Money(clamping: 0) }

    func add(_ other: Money) -> Money {
        Money(clamping: amount + other.amount)
    }

    func subtract(_ other: Money) throws -> Money {
        try Money(amount - other.amount)
    }

    /// Raw signed difference; unlike `subtract`, this may be negative.
    func difference(_ other: Money) -> Int {
        amount - other.amount
    }

    func isGreaterThan(_ other: Money) -> Bool {
        amount > other.amount
    }

    static func < (lhs: Money, rhs: Money) -> Bool { lhs.amount < rhs.amount }
}
