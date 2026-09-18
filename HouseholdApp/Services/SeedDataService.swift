import Foundation
import SwiftData

/// Mirrors `database/seeders/CategorySeeder.php`: seeds the same six
/// default categories on first launch.
enum SeedDataService {
    static let defaultCategoryNames = ["食費", "交通費", "家賃", "光熱費", "娯楽", "給料"]

    static func seedDefaultCategoriesIfNeeded(context: ModelContext) {
        let descriptor = FetchDescriptor<Category>()
        let existingCount = (try? context.fetchCount(descriptor)) ?? 0
        guard existingCount == 0 else { return }

        for name in defaultCategoryNames {
            context.insert(Category(name: name))
        }
        try? context.save()
    }
}
