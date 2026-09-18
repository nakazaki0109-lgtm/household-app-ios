import SwiftUI

/// A category name + amount + horizontal percentage bar, used in the
/// カテゴリ別支出 breakdown on the monthly report (mirrors the Laravel
/// view's inline progress bar).
struct CategoryProgressRow: View {
    let name: String
    let amountText: String
    let percentage: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(name)
                    .font(.subheadline)
                Spacer()
                Text(amountText)
                    .font(.subheadline.monospacedDigit())
                Text("\(percentage, specifier: "%.1f")%")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .frame(width: 50, alignment: .trailing)
            }
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color(.systemGray5))
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.accentColor)
                        .frame(width: geometry.size.width * min(max(percentage / 100, 0), 1))
                }
            }
            .frame(height: 8)
        }
    }
}
