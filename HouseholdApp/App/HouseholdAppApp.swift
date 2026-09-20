import SwiftUI
import SwiftData

@main
struct HouseholdAppApp: App {
    let modelContainer: ModelContainer
    private let launchOptions: LaunchOptions

    init() {
        let options = LaunchOptions(arguments: ProcessInfo.processInfo.arguments)
        launchOptions = options
        let configuration = ModelConfiguration(isStoredInMemoryOnly: options.usesSampleData)
        do {
            modelContainer = try ModelContainer(
                for: Category.self, Transaction.self, MonthlyBudget.self, CategoryBudget.self,
                configurations: configuration
            )
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
        let context = modelContainer.mainContext
        SeedDataService.seedDefaultCategoriesIfNeeded(context: context)
        if options.usesSampleData {
            try? ScreenshotSampleDataService.seed(month: TargetMonth.current(), context: context)
        }
    }

    var body: some Scene {
        WindowGroup {
            RootView(initialTab: launchOptions.initialTab)
        }
        .modelContainer(modelContainer)
    }
}
