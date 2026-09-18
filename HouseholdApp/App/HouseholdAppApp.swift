import SwiftUI
import SwiftData

@main
struct HouseholdAppApp: App {
    let modelContainer: ModelContainer

    init() {
        do {
            modelContainer = try ModelContainer(for: Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self)
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
        SeedDataService.seedDefaultCategoriesIfNeeded(context: modelContainer.mainContext)
    }

    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .modelContainer(modelContainer)
    }
}
