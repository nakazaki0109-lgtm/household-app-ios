import Foundation
import SwiftData

/// Mirrors the Laravel `transactions` table. `category` is optional —
/// deleting a category nullifies it here rather than deleting the
/// transaction, matching the Laravel `nullOnDelete` foreign key.
@Model
final class Transaction {
    var id: UUID
    var type: TransactionType
    /// Whole yen, non-negative (enforced at the service layer via `Money`).
    var amount: Int
    var transactionDate: Date
    var memo: String?
    var createdAt: Date

    var category: Category?

    init(type: TransactionType, amount: Int, transactionDate: Date, memo: String?, category: Category?) {
        self.id = UUID()
        self.type = type
        self.amount = amount
        self.transactionDate = transactionDate
        self.memo = memo
        self.category = category
        self.createdAt = Date()
    }
}
