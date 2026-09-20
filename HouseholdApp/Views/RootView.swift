import SwiftUI

/// Tab bar replacing the Laravel app's page-to-page links (it has no
/// persistent navigation chrome of its own — each screen just links to the
/// others). 月別集計 is the home screen, matching `/` → `/reports/monthly`.
struct RootView: View {
    @State private var selection: Int

    init(initialTab: Int = 0) {
        _selection = State(initialValue: initialTab)
    }

    var body: some View {
        TabView(selection: $selection) {
            MonthlySummaryView()
                .tabItem { Label("月別集計", systemImage: "chart.bar") }
                .tag(0)

            TransactionListView()
                .tabItem { Label("収支一覧", systemImage: "list.bullet") }
                .tag(1)

            BudgetMenuView()
                .tabItem { Label("予算設定", systemImage: "yensign.circle") }
                .tag(2)
        }
    }
}

#Preview {
    RootView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
