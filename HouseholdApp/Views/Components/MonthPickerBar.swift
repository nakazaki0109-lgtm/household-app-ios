import SwiftUI

/// Prev/next month stepper, replacing the Laravel views' `<input
/// type="month">` with an idiomatic SwiftUI control.
struct MonthPickerBar: View {
    @Binding var month: TargetMonth

    var body: some View {
        HStack {
            Button {
                shift(by: -1)
            } label: {
                Image(systemName: "chevron.left")
            }

            Spacer()

            Text(displayText)
                .font(.headline)
                .contentTransition(.numericText())

            Spacer()

            Button {
                shift(by: 1)
            } label: {
                Image(systemName: "chevron.right")
            }
        }
        .padding(.horizontal)
        .animation(.default, value: month)
    }

    private var displayText: String {
        let date = month.monthDate
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ja_JP")
        formatter.dateFormat = "yyyy年M月"
        return formatter.string(from: date)
    }

    private func shift(by value: Int) {
        let calendar = Calendar.current
        guard let newDate = calendar.date(byAdding: .month, value: value, to: month.monthDate) else { return }
        month = TargetMonth(date: newDate)
    }
}
