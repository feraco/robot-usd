# Animated Robot USD/USDZ Files

This repository contains examples of animated USD files and their USDZ conversions for use in Xcode with RealityKit.

## Files

- `examples/animated_robot.usda` - A simple animated robot in USD format
- `examples/animated_robot.usdz` - The simple robot converted to USDZ format
- `examples/complex_robot.usda` - A more complex animated robot with multiple moving parts in USD format
- `examples/complex_robot.usdz` - The complex robot converted to USDZ format

## Scripts

- `examples/create_animated_robot.py` - Script to create the simple animated robot
- `examples/create_complex_robot.py` - Script to create the complex animated robot
- `examples/convert_to_usdz.py` - Script to convert USD files to USDZ format

## How to Use in Xcode with RealityKit

### Adding USDZ Files to Your Xcode Project

1. Open your Xcode project
2. In the Project Navigator, right-click on your project or a group where you want to add the USDZ files
3. Select "Add Files to [Your Project Name]..."
4. Navigate to and select the USDZ files
5. Make sure "Copy items if needed" is checked
6. Click "Add"

### Loading USDZ Files in RealityKit

Here's a simple example of how to load and display a USDZ file in RealityKit:

```swift
import SwiftUI
import RealityKit

struct ContentView: View {
    var body: some View {
        ARViewContainer()
            .edgesIgnoringSafeArea(.all)
    }
}

struct ARViewContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Load the USDZ model
        let modelEntity = try! ModelEntity.load(named: "complex_robot.usdz")
        
        // Create an anchor for the model
        let anchor = AnchorEntity(plane: .horizontal)
        anchor.addChild(modelEntity)
        
        // Add the anchor to the scene
        arView.scene.addAnchor(anchor)
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
}
```

### Controlling Animation Playback

To control the animation playback of your USDZ model:

```swift
// Get the animation from the model
if let animation = modelEntity.availableAnimations.first {
    // Play the animation
    modelEntity.playAnimation(animation.repeat())
    
    // Or play with specific options
    modelEntity.playAnimation(animation, transitionDuration: 0.5, startsPaused: false)
    
    // To pause the animation
    // modelEntity.pauseAnimation()
    
    // To resume the animation
    // modelEntity.resumeAnimation()
    
    // To stop the animation
    // modelEntity.stopAllAnimations()
}
```

### Scaling and Positioning

You can adjust the scale and position of your model:

```swift
// Scale the model
modelEntity.scale = SIMD3<Float>(0.1, 0.1, 0.1)

// Position the model
modelEntity.position = SIMD3<Float>(0, 0, -0.5)

// Rotate the model
modelEntity.orientation = simd_quatf(angle: .pi/2, axis: SIMD3<Float>(0, 1, 0))
```

## Creating Your Own Animated USDZ Files

To create your own animated USDZ files:

1. Create a USD file with animation using the provided scripts as examples
2. Convert the USD file to USDZ format using the `convert_to_usdz.py` script:

```bash
python3 examples/convert_to_usdz.py your_animated_file.usda
```

## Requirements

- USD Core library (`pip install usd-core`)
- Python 3.6+

## Notes

- USDZ files are compatible with iOS/iPadOS 12+ and macOS 10.14+
- RealityKit is available on iOS/iPadOS 13+ and macOS 10.15+
- Make sure your animations have a reasonable number of keyframes for smooth playback
- For AR experiences, keep your models reasonably sized and optimized