# Setting Up an Xcode Project for USDZ Models with RealityKit

This guide will walk you through setting up a new Xcode project to use the animated USDZ robot models with RealityKit.

## Prerequisites

- Xcode 12 or later
- iOS 14 or later
- A physical iOS device (for testing AR features)
- The USDZ files from this package

## Step 1: Create a New Xcode Project

1. Open Xcode
2. Select "File" > "New" > "Project..."
3. Choose "App" under the iOS tab
4. Click "Next"
5. Enter your project details:
   - Product Name: "RobotAR" (or any name you prefer)
   - Interface: "SwiftUI"
   - Life Cycle: "SwiftUI App"
   - Language: "Swift"
6. Click "Next" and choose a location to save your project
7. Click "Create"

## Step 2: Add USDZ Files to Your Project

1. In Xcode, right-click on your project in the Navigator panel
2. Select "Add Files to [Your Project Name]..."
3. Navigate to and select the USDZ files (b2_animated.usdz, g1_animated.usdz)
4. Make sure "Copy items if needed" is checked
5. Click "Add"

## Step 3: Configure Project for AR

1. Select your project in the Navigator panel
2. Select your app target
3. Go to the "Info" tab
4. Add the following keys to your Info.plist:
   - Privacy - Camera Usage Description: "This app uses the camera for Augmented Reality."
   - Add this by clicking the "+" button next to any existing key and typing the key name

## Step 4: Add the RobotARView.swift File

1. Right-click on your project in the Navigator panel
2. Select "Add Files to [Your Project Name]..."
3. Navigate to and select the RobotARView.swift file
4. Make sure "Copy items if needed" is checked
5. Click "Add"

## Step 5: Update Your ContentView.swift

1. Open ContentView.swift
2. Replace its contents with:

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

## Step 6: Run the App

1. Connect your iOS device to your Mac
2. Select your device from the device dropdown in Xcode
3. Click the "Run" button (or press Cmd+R)
4. When the app launches, it will request camera access - grant permission
5. Point your camera at a horizontal surface
6. Tap on the surface to place the robot model
7. Use the buttons at the bottom to switch between different robot models

## Customizing the App

### Changing the Default Model

To change which model appears by default, modify the `@State` variable in RobotARView.swift:

```swift
@State private var modelName: String = "g1_animated" // Change to your preferred model
```

### Adjusting Model Scale

If the model appears too large or too small, adjust the scale value:

```swift
@State private var modelScale: Float = 0.05 // Smaller number = smaller model
```

### Adding More Models

1. Add additional USDZ files to your project
2. Add new buttons to the HStack in RobotARView.swift:

```swift
Button(action: {
    modelName = "your_new_model_name"
    modelScale = 0.1 // Adjust as needed
}) {
    Text("New Model")
        .padding()
        .background(modelName == "your_new_model_name" ? Color.blue : Color.gray)
        .foregroundColor(.white)
        .cornerRadius(8)
}
```

## Troubleshooting

### Model Not Appearing

1. Make sure the USDZ files are properly added to your project and included in the target's "Copy Bundle Resources" build phase
2. Check that the model name in your code matches the filename (without extension)
3. Try adjusting the scale of the model - it might be too large or too small to be visible

### AR Features Not Working

1. Make sure you're testing on a physical device (AR won't work in the simulator)
2. Ensure you've added the required privacy description for camera usage
3. Make sure your device supports ARKit (iPhone 6s or later, running iOS 14+)

### Animation Not Playing

1. Check if the model has animations by adding this debug code:
   ```swift
   print("Available animations: \(modelEntity.availableAnimations.count)")
   ```
2. If no animations are found, the USDZ file might not contain animation data
3. Try creating a new animated USDZ file with the provided script