import SwiftUI
import SwiftData

/// Mirrors `Budgets\CategoryEdit` (`/budgets/category-edit`): set a budget
/// per category for a given month. Blank fields are skipped on save,
/// leaving any previously-saved value untouched (matches the Laravel
/// behavior — there is no way to "unset" a category budget from this
/// screen).
struct CategoryBudgetEditView: View {
    @Environment(\.modelContext) private var context

    @State var month: TargetMonth
    @State private var amountTexts: [PersistentIdentifier: String] = [:]
    @State private var savedMessage: String?
    @State private var errorMessage: String?

    private var categories: [Category] {
        CategoryService.fetchAll(context: context)
    }

    var body: some View {
        Form {
            Section {
                MonthPickerBar(month: $month)
                    .listRowInsets(EdgeInsets())
                    .padding(.vertical, 8)
            }

            Section("カテゴリ別予算") {
                ForEach(categories) { category in
                    HStack {
                        Text(category.name)
                        Spacer()
                        TextField("予算額を入力", text: binding(for: category))
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                            .frame(width: 120)
                    }
                }
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
        .navigationTitle("カテゴリ別予算設定")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("保存") { save() }
            }
        }
        .onAppear { loadAmounts() }
        .onChange(of: month) { _, _ in loadAmounts() }
    }

    private func binding(for category: Category) -> Binding<String> {
        Binding(
            get: { amountTexts[category.persistentModelID] ?? "" },
            set: { amountTexts[category.persistentModelID] = $0 }
        )
    }

    private func loadAmounts() {
        savedMessage = nil
        let existing = BudgetService.categoryBudgetAmounts(for: month, context: context)
        amountTexts = existing.mapValues(String.init)
    }

    private func save() {
        errorMessage = nil
        do {
            for category in categories {
                guard let text = amountTexts[category.persistentModelID], !text.isEmpty else { continue }
                guard let amount = Int(text) else {
                    errorMessage = "\(category.name)の予算額は数値で入力してください。"
                    return
                }
                try BudgetService.saveCategoryBudget(category: category, month: month, amount: amount, context: context)
            }
            savedMessage = "カテゴリ別予算を保存しました。"
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    NavigationStack {
        CategoryBudgetEditView(month: .current())
    }
    .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
