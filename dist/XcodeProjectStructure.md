# Xcode Project Structure for RealityKit Robot Demo

This document outlines how to structure an Xcode project to use the animated robot USDZ files with RealityKit.

## Project Setup

1. Open Xcode and create a new project
2. Select "App" under the iOS tab
3. Name your project (e.g., "RobotARDemo")
4. Choose SwiftUI for the interface
5. Make sure "Use Core Data" is unchecked

## Adding USDZ Files

1. Drag and drop the USDZ files (`animated_robot.usdz` and `complex_robot.usdz`) into your Xcode project
2. When prompted, check "Copy items if needed" and add to your main target

## Project Structure

Your project should have a structure similar to this:

```
RobotARDemo/
├── Assets.xcassets/
├── animated_robot.usdz
├── complex_robot.usdz
├── RobotARDemoApp.swift
├── ContentView.swift
├── RobotARView.swift
└── Info.plist
```

## Required Capabilities

Add the following to your `Info.plist` file:

```xml
<key>NSCameraUsageDescription</key>
<string>This app uses the camera for Augmented Reality.</string>
```

## App Implementation

1. Copy the `RobotARView.swift` file into your project
2. Update your `ContentView.swift` to use the `RobotARView`:

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        RobotARView()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
```

3. Update your app entry point in `RobotARDemoApp.swift`:

```swift
import SwiftUI

@main
struct RobotARDemoApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Building and Running

1. Select an iOS device as your build target (AR requires a physical device)
2. Build and run the app
3. When the app launches, it will request camera access
4. Point the camera at a horizontal surface
5. Tap either "Simple Robot" or "Complex Robot" to place the animated model

## Troubleshooting

- If the model doesn't appear, make sure you're pointing at a well-lit horizontal surface
- If animations don't play, check that the USDZ files were properly added to the project
- If you get build errors, make sure you've added the required privacy description for camera usage
- For deployment issues, ensure your device is running iOS 13 or later