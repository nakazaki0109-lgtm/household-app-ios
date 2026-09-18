import SwiftUI

/// Entry point for the two budget-editing screens. The Laravel app links to
/// `/budgets/edit` and `/budgets/category-edit` from the monthly report
/// page; this tab provides the same two destinations directly.
struct BudgetMenuView: View {
    @State private var month: TargetMonth = .current()

    var body: some View {
        NavigationStack {
            List {
                NavigationLink {
                    MonthlyBudgetEditView(month: month)
                } label: {
                    Label("月予算設定", systemImage: "yensign.circle")
                }
                NavigationLink {
                    CategoryBudgetEditView(month: month)
                } label: {
                    Label("カテゴリ別予算設定", systemImage: "chart.pie")
                }
            }
            .navigationTitle("予算設定")
        }
    }
}

#Preview {
    BudgetMenuView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
