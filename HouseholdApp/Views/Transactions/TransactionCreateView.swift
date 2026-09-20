import SwiftUI
import SwiftData

/// Mirrors `Transactions\Create` (`/transactions/create`): 種別 / 金額 / 日付
/// / カテゴリ / メモ form. On save, the Laravel app redirects to the monthly
/// report; here we simply dismiss back to the presenting screen.
struct TransactionCreateView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss

    @State private var type: TransactionType = .expense
    @State private var amountText: String = ""
    @State private var transactionDate: Date = Date()
    @State private var selectedCategory: Category?
    @State private var memo: String = ""
    @State private var errorMessage: String?

    private var categories: [Category] {
        CategoryService.fetchAll(context: context)
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("種別") {
                    Picker("種別", selection: $type) {
                        ForEach(TransactionType.allCases) { type in
                            Text(type.label).tag(type)
                        }
                    }
                    .pickerStyle(.segmented)
                    .accessibilityIdentifier(AccessibilityID.TransactionCreate.typePicker)
                }

                Section("金額") {
                    TextField("金額", text: $amountText)
                        .keyboardType(.numberPad)
                        .accessibilityIdentifier(AccessibilityID.TransactionCreate.amountField)
                }

                Section("日付") {
                    DatePicker("日付", selection: $transactionDate, displayedComponents: .date)
                        .datePickerStyle(.compact)
                        .accessibilityIdentifier(AccessibilityID.TransactionCreate.datePicker)
                }

                Section("カテゴリ") {
                    Picker("カテゴリ", selection: $selectedCategory) {
                        Text("選択してください").tag(nil as Category?)
                        ForEach(categories) { category in
                            Text(category.name).tag(category as Category?)
                        }
                    }
                    .accessibilityIdentifier(AccessibilityID.TransactionCreate.categoryPicker)
                }

                Section("メモ") {
                    TextField("メモ（任意）", text: $memo, axis: .vertical)
                        .accessibilityIdentifier(AccessibilityID.TransactionCreate.memoField)
                }

                if let errorMessage {
                    Section {
                        Text(errorMessage)
                            .foregroundStyle(.red)
                            .font(.footnote)
                            .accessibilityIdentifier(AccessibilityID.TransactionCreate.errorMessage)
                    }
                }
            }
            .navigationTitle("収支登録")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("キャンセル") { dismiss() }
                        .accessibilityIdentifier(AccessibilityID.TransactionCreate.cancelButton)
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }
                        .accessibilityIdentifier(AccessibilityID.TransactionCreate.saveButton)
                }
            }
        }
    }

    private func save() {
        guard let amount = Int(amountText) else {
            errorMessage = "金額は数値で入力してください。"
            return
        }
        do {
            try TransactionService.save(
                type: type,
                amount: amount,
                transactionDate: transactionDate,
                category: selectedCategory,
                memo: memo,
                context: context
            )
            dismiss()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    TransactionCreateView()
        .modelContainer(for: [Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self], inMemory: true)
}
