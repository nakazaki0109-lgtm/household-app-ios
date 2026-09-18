import SwiftUI
import SwiftData

/// Mirrors `Transactions\Index` (`/transactions`): a full list of all
/// transactions, newest first.
struct TransactionListView: View {
    @Environment(\.modelContext) private var context
    @State private var showingCreateTransaction = false

    private var transactions: [Transaction] {
        TransactionService.fetchAll(context: context)
    }

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
