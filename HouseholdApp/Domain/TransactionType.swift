import Foundation

/// Mirrors `App\Domain\Transaction\TransactionType` from the Laravel app.
enum TransactionType: String, Codable, CaseIterable, Identifiable {
    case income
    case expense

    var id: String { rawValue }

    var label: String {
        switch self {
        case .income: return "収入"
        case .expense: return "支出"
        }
    }
}
