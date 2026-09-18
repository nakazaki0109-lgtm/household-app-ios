import SwiftUI

/// Tab bar replacing the Laravel app's page-to-page links (it has no
/// persistent navigation chrome of its own — each screen just links to the
/// others). 月別集計 is the home screen, matching `/` → `/reports/monthly`.
struct RootView: View {
    var body: some View {
        TabView {
            MonthlySummaryView()
                .tabItem { Label("月別集計", systemImage: "chart.bar") }

            TransactionListView()
                .tabItem { Label("収支一覧", systemImage: "list.bullet") }

            BudgetMenuView()
                .tabItem { Label("予算設定", systemImage: "yensign.circle") }
        }
    }
}

#Preview {
    RootView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
