import SwiftUI
import SwiftData

/// Mirrors `Reports\MonthlySummary` (`/reports/monthly`) — the app's home
/// screen: month selector, income/expense/balance tiles, whole-month budget
/// tiles, category expense breakdown, the month's transaction list, and the
/// per-category budget comparison table.
struct MonthlySummaryView: View {
    @Environment(\.modelContext) private var context
    @State private var month: TargetMonth = .current()
    @State private var showingCreateTransaction = false

    private var summary: ReportService.MonthlySummary {
        ReportService.monthlySummary(for: month, context: context)
    }

    private var budgetStatus: BudgetStatus {
        BudgetService.monthlyBudgetStatus(for: month, expenseTotal: summary.expenseTotal, context: context)
    }

    private var categoryComparisons: [BudgetService.CategoryComparison] {
        BudgetService.categoryComparisons(for: month, context: context)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    MonthPickerBar(month: $month)

                    quickActions

                    tileGrid(
                        [
                            ("収入合計", YenFormatter.string(summary.incomeTotal), .green),
                            ("支出合計", YenFormatter.string(summary.expenseTotal), .red),
                            ("収支差額", YenFormatter.signedString(summary.balance), summary.balance >= 0 ? .blue : .red),
                        ]
                    )

                    tileGrid(
                        [
                            ("今月の予算", YenFormatter.string(budgetStatus.budgetAmount), .primary),
                            ("残額", YenFormatter.signedString(budgetStatus.remainingAmount), budgetStatus.remainingAmount >= 0 ? .green : .red),
                            ("予算判定", budgetStatus.isExceeded ? "超過" : "予算内", budgetStatus.isExceeded ? .red : .green),
                        ]
                    )

                    categoryBreakdownSection
                    transactionListSection
                    categoryBudgetComparisonSection
                }
                .padding()
            }
            .navigationTitle("月別集計")
            .sheet(isPresented: $showingCreateTransaction) {
                TransactionCreateView()
            }
        }
    }

    private var quickActions: some View {
        HStack(spacing: 12) {
            Button {
                showingCreateTransaction = true
            } label: {
                Label("収支を登録", systemImage: "plus.circle.fill")
            }
            .buttonStyle(.borderedProminent)

            NavigationLink {
                MonthlyBudgetEditView(month: month)
            } label: {
                Label("予算設定", systemImage: "yensign.circle")
            }
            .buttonStyle(.bordered)

            NavigationLink {
                CategoryBudgetEditView(month: month)
            } label: {
                Label("カテゴリ別予算", systemImage: "chart.pie")
            }
            .buttonStyle(.bordered)
        }
        .font(.subheadline)
    }

    private func tileGrid(_ tiles: [(String, String, Color)]) -> some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            ForEach(tiles, id: \.0) { tile in
                SummaryTileView(title: tile.0, value: tile.1, color: tile.2)
            }
        }
    }

    private var categoryBreakdownSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("カテゴリ別支出")
                .font(.headline)
            if summary.categorySummaries.isEmpty {
                Text("この月のカテゴリ別支出データはありません。")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                VStack(spacing: 14) {
                    ForEach(summary.categorySummaries) { item in
                        CategoryProgressRow(
                            name: item.categoryName,
                            amountText: YenFormatter.string(item.totalAmount),
                            percentage: item.percentage(ofExpenseTotal: summary.expenseTotal)
                        )
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var transactionListSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("この月の収支")
                .font(.headline)
            if summary.transactions.isEmpty {
                Text("この月のデータはありません。")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                VStack(spacing: 0) {
                    ForEach(summary.transactions) { transaction in
                        TransactionRow(transaction: transaction)
                        if transaction.id != summary.transactions.last?.id {
                            Divider()
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var categoryBudgetComparisonSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("カテゴリ別予算比較")
                .font(.headline)
            if categoryComparisons.isEmpty {
                Text("カテゴリがありません。")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                VStack(spacing: 0) {
                    ForEach(categoryComparisons) { comparison in
                        CategoryBudgetComparisonRow(comparison: comparison)
                        if comparison.id != categoryComparisons.last?.id {
                            Divider()
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private struct CategoryBudgetComparisonRow: View {
    let comparison: BudgetService.CategoryComparison

    var body: some View {
        HStack {
            Text(comparison.category.name)
                .font(.subheadline)
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                Text("支出 \(YenFormatter.string(comparison.status.spentAmount)) / 予算 \(YenFormatter.string(comparison.status.budgetAmount))")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(comparison.status.isExceeded ? "超過" : "予算内")
                    .font(.caption.bold())
                    .foregroundStyle(comparison.status.isExceeded ? .red : .green)
            }
        }
        .padding(.vertical, 8)
    }
}

#Preview {
    MonthlySummaryView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
