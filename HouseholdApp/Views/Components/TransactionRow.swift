import SwiftUI

/// A single row in a transaction list (日付 / 種別 / カテゴリ / 金額 / メモ),
/// used by both `TransactionListView` and the monthly report's transaction
/// table.
struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(DateFormatter.dateDisplay.string(from: transaction.transactionDate))
                        .font(.subheadline)
                    Text(transaction.type.label)
                        .font(.caption.bold())
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(transaction.type == .income ? Color.green.opacity(0.15) : Color.red.opacity(0.15))
                        .foregroundStyle(transaction.type == .income ? .green : .red)
                        .clipShape(Capsule())
                }
                Text(transaction.category?.name ?? "-")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                if let memo = transaction.memo, !memo.isEmpty {
                    Text(memo)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
            Text(YenFormatter.string(transaction.amount))
                .font(.subheadline.monospacedDigit())
                .foregroundStyle(transaction.type == .income ? .green : .primary)
        }
        .padding(.vertical, 8)
    }
}
