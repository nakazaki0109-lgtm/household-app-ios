import SwiftUI
import SwiftData

/// Mirrors `Transactions\Index` (`/transactions`): a full list of all
/// transactions, newest first.
struct TransactionListView: View {
    // context.fetch の結果は SwiftUI が変更を追跡しない。保存後に一覧が古いままになるので @Query で受ける。
    @Query(sort: TransactionService.newestFirst) private var transactions: [Transaction]
    @State private var showingCreateTransaction = false

    var body: some View {
        NavigationStack {
            Group {
                if transactions.isEmpty {
                    ContentUnavailableView(
                        "まだ収支データがありません。",
                        systemImage: "yensign.circle",
                        description: Text("右上の追加ボタンから登録できます。")
                    )
                } else {
                    List {
                        ForEach(transactions) { transaction in
                            TransactionRow(transaction: transaction)
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("収支一覧")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingCreateTransaction = true
                    } label: {
                        Label("新規登録", systemImage: "plus")
                    }
                    .accessibilityIdentifier(AccessibilityID.TransactionList.addButton)
                }
            }
            .sheet(isPresented: $showingCreateTransaction) {
                TransactionCreateView()
            }
        }
    }
}

#Preview {
    TransactionListView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
