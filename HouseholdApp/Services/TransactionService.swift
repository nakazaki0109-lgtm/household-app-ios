import Foundation
import SwiftData

/// Mirrors `Transactions\Create` (form validation) and
/// `SaveTransactionUseCase` from the Laravel app.
enum TransactionService {
    enum ValidationError: Swift.Error, LocalizedError {
        case amountTooSmall

        var errorDescription: String? {
            switch self {
            case .amountTooSmall: return "金額は1以上を入力してください。"
            }
        }
    }

    /// Saves a new transaction. `amount` must be >= 1, matching the
    /// Livewire form rule (stricter than `Money`, which only forbids
    /// negative values).
    @discardableResult
    static func save(
        type: TransactionType,
        amount: Int,
        transactionDate: Date,
        category: Category?,
        memo: String?,
        context: ModelContext
    ) throws -> Transaction {
        guard amount >= 1 else { throw ValidationError.amountTooSmall }
        _ = try Money(amount)

        let trimmedMemo = memo?.trimmingCharacters(in: .whitespacesAndNewlines)
        let transaction = Transaction(
            type: type,
            amount: amount,
            transactionDate: transactionDate,
            memo: (trimmedMemo?.isEmpty ?? true) ? nil : trimmedMemo,
            category: category
        )
        context.insert(transaction)
        try context.save()
        return transaction
    }

    /// All transactions, newest first (matches `Transactions\Index`, which
    /// orders by `transaction_date desc, id desc`).
    static func fetchAll(context: ModelContext) -> [Transaction] {
        let descriptor = FetchDescriptor<Transaction>(
            sortBy: [SortDescriptor(\.transactionDate, order: .reverse), SortDescriptor(\.createdAt, order: .reverse)]
        )
        return (try? context.fetch(descriptor)) ?? []
    }

    /// Transactions within a given month, newest first (matches
    /// `TransactionRepositoryInterface::findByUserAndMonth`).
    static func fetch(for month: TargetMonth, context: ModelContext) -> [Transaction] {
        let interval = month.dateInterval
        return fetchAll(context: context).filter { $0.transactionDate >= interval.start && $0.transactionDate < interval.end }
    }
}
