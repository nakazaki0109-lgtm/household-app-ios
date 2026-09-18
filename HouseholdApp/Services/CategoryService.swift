import Foundation
import SwiftData

/// Mirrors `App\Repositories\CategoryRepositoryInterface::findByUser` —
/// there is only one (local) user, so this simply returns all categories.
enum CategoryService {
    static func fetchAll(context: ModelContext) -> [Category] {
        let descriptor = FetchDescriptor<Category>(sortBy: [SortDescriptor(\.name)])
        return (try? context.fetch(descriptor)) ?? []
    }
}
