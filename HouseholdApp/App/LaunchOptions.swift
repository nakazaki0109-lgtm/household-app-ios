import Foundation

/// スクリーンショット撮影用の起動引数。通常起動では指定されないので何も変わらない。
struct LaunchOptions: Equatable {
    static let sampleDataFlag = "-ScreenshotSampleData"
    static let tabFlag = "-ScreenshotTab"
    static let tabCount = 3

    let usesSampleData: Bool
    let initialTab: Int

    init(arguments: [String]) {
        usesSampleData = arguments.contains(LaunchOptions.sampleDataFlag)
        initialTab = LaunchOptions.parseTab(arguments: arguments)
    }

    private static func parseTab(arguments: [String]) -> Int {
        guard let flagIndex = arguments.firstIndex(of: tabFlag) else { return 0 }
        let valueIndex = arguments.index(after: flagIndex)
        guard valueIndex < arguments.endIndex, let tab = Int(arguments[valueIndex]) else { return 0 }
        guard (0..<tabCount).contains(tab) else { return 0 }
        return tab
    }
}
