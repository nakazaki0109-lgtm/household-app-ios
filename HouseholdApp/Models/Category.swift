import Foundation
import SwiftData

/// Mirrors the Laravel `categories` table. This app is single-user (local
/// only), so there is no `user_id` column.
@Model
final class Category {
    var id: UUID
    var name: String
    var createdAt: Date

    @Relationship(deleteRule: .nullify, inverse: \Transaction.category)
    var transactions: [Transaction]? = []

    @Relationship(deleteRule: .cascade, inverse: \CategoryBudget.category)
    var categoryBudgets: [CategoryBudget]? = []

    init(name: String) {
        self.id = UUID()
        self.name = name
        self.createdAt = Date()
    }
}
