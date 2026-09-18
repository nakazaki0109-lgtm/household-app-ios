import SwiftUI
import SwiftData

/// Mirrors `Budgets\Edit` (`/budgets/edit`): set the whole-month budget for
/// a given month.
struct MonthlyBudgetEditView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss

    @State var month: TargetMonth
    @State private var amountText: String = ""
    @State private var errorMessage: String?
    @State private var savedMessage: String?

    var body: some View {
        Form {
            Section {
                MonthPickerBar(month: $month)
                    .listRowInsets(EdgeInsets())
                    .padding(.vertical, 8)
            }

            Section("月予算") {
                TextField("月予算", text: $amountText)
                    .keyboardType(.numberPad)
            }

            if let errorMessage {
                Section {
                    Text(errorMessage).foregroundStyle(.red).font(.footnote)
                }
            }

            if let savedMessage {
                Section {
                    Text(savedMessage).foregroundStyle(.green).font(.footnote)
                }
            }
        }
        .navigationTitle("月予算設定")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("保存") { save() }
            }
        }
        .onAppear { loadAmount() }
        .onChange(of: month) { _, _ in loadAmount() }
    }

    private func loadAmount() {
        savedMessage = nil
        let existing = BudgetService.monthlyBudgetAmount(for: month, context: context)
        amountText = existing.map(String.init) ?? ""
    }

    private func save() {
        let amount = Int(amountText) ?? 0
        do {
            try BudgetService.saveMonthlyBudget(month: month, amount: amount, context: context)
            errorMessage = nil
            savedMessage = "月予算を保存しました。"
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    NavigationStack {
        MonthlyBudgetEditView(month: .current())
    }
    .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
