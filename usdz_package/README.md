# Using Animated USDZ Files in Xcode with RealityKit

This guide explains how to use the animated USDZ files in your Xcode project with RealityKit.

## Available USDZ Files

The repository now includes the following animated USDZ files:

- `cf2x_animated.usdz` - Animated Crazyflie drone with spinning propellers and colored parts
- `b2_animated.usdz` - Animated Unitree B2 robot
- `g1_animated.usdz` - Animated Unitree G1 robot
- `custom_drone_example.usdz` - Example of a custom drone created with the create_drone.py script

## Creating Your Own Animated USDZ Files

### From Existing USD Files

#### Using Original USD Geometry with Custom Colors

If you want to create an animated USDZ file that preserves all the original geometry but adds custom colors and properly positioned propellers, you can use the `create_colored_crazyflie.py` script. This script:

1. Copies all the original geometry from the source USD file
2. Adds custom colors to different parts (body, propellers, battery, etc.)
3. Correctly positions the propellers over each motor
4. Adds rotation animation to the propellers (spinning around their Z-axis)
5. Creates both USDA and USDZ files

This approach is ideal when you want to maintain the original geometry but customize the colors and ensure proper propeller animation.

#### iOS and SceneKit Compatible Animations

For better compatibility with iOS, macOS, and SceneKit, we provide three specialized scripts:

1. **`create_scenekit_compatible_crazyflie.py`**: Creates a USDZ file optimized for SceneKit with proper animation hierarchy.
2. **`create_explicit_animation_crazyflie.py`**: Uses explicit animation on the propeller meshes for better compatibility.
3. **`create_ios_compatible_crazyflie.py`**: Uses iOS-specific animation techniques and settings for optimal compatibility.

These scripts produce USDZ files that should work well when viewed directly in iOS/macOS or when imported into Xcode projects with RealityKit or SceneKit.

#### Using Original USD Geometry with Original Materials

If you want to create an animated USDZ file that preserves all the original geometry and materials from a USD file, you can use the `create_original_animated_crazyflie.py` script. This script:

1. Copies all the original geometry and materials from the source USD file
2. Adds rotation animation to the propellers
3. Adds a subtle hovering motion to the entire drone
4. Creates both USDA and USDZ files

This approach is ideal when you want to maintain the exact appearance of the original USD model while adding animation.

You can create animated USDZ files from existing USD files using the provided script:

```bash
python create_animated_usdz.py input.usd [output.usdz] [--duration 3] [--fps 24]
```

Arguments:
- `input.usd` - Path to the input USD file
- `output.usdz` - (Optional) Path to the output USDZ file (default: input_animated.usdz)
- `--duration` - (Optional) Animation duration in seconds (default: 3)
- `--fps` - (Optional) Frames per second (default: 24)

### Creating a Custom Drone

You can also create a custom animated drone with spinning propellers using the drone creation script:

```bash
python create_drone.py [output.usdz] [--duration 3] [--fps 24] [--body-color 0.1,0.1,0.1] [--prop1-color 0.8,0.0,0.0] [--prop2-color 0.0,0.0,0.8]
```

Arguments:
- `output.usdz` - (Optional) Path to the output USDZ file (default: drone_animated.usdz)
- `--duration` - (Optional) Animation duration in seconds (default: 3)
- `--fps` - (Optional) Frames per second (default: 24)
- `--body-color` - (Optional) RGB color for the drone body (default: 0.1,0.1,0.1)
- `--prop1-color` - (Optional) RGB color for propellers 1 and 3 (default: 0.8,0.0,0.0)
- `--prop2-color` - (Optional) RGB color for propellers 2 and 4 (default: 0.0,0.0,0.8)

Example:
```bash
# Create a drone with a green body and yellow/purple propellers
python create_drone.py my_drone.usdz --body-color 0.0,0.5,0.0 --prop1-color 1.0,1.0,0.0 --prop2-color 0.5,0.0,0.5
```

## Using USDZ Files in Xcode

### 1. Add USDZ Files to Your Xcode Project

1. Open your Xcode project
2. Drag and drop the USDZ files into your project navigator
3. When prompted, check "Copy items if needed" and select your target

### 2. Load and Display USDZ Models in SwiftUI with RealityKit

Here's a basic example of how to display a USDZ model in AR using SwiftUI and RealityKit:

```swift
import SwiftUI
import RealityKit
import ARKit

struct RobotARView: View {
    var body: some View {
        ARViewContainer()
            .edgesIgnoringSafeArea(.all)
    }
}

struct ARViewContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Configure AR session
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal]
        arView.session.run(config)
        
        // Load the USDZ model
        let modelName = "b2_animated" // Change to your model name without extension
        
        // Create anchor for the model
        let anchor = AnchorEntity(plane: .horizontal)
        
        // Load and add the model
        if let modelEntity = try? ModelEntity.load(named: modelName) {
            // Scale the model if needed
            modelEntity.scale = SIMD3<Float>(0.1, 0.1, 0.1)
            
            // Add the model to the anchor
            anchor.addChild(modelEntity)
            
            // Add the anchor to the scene
            arView.scene.addAnchor(anchor)
        }
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
}

struct RobotARView_Previews: PreviewProvider {
    static var previews: some View {
        RobotARView()
    }
}
```

### 3. Handling Animations

The USDZ files contain built-in animations that will play automatically when loaded. If you want to control the animation:

```swift
// Load the model
if let modelEntity = try? ModelEntity.load(named: modelName) {
    // Access the animation
    if let animation = modelEntity.availableAnimations.first {
        // Play the animation
        modelEntity.playAnimation(animation.repeat())
        
        // Or control it more precisely
        // modelEntity.playAnimation(animation.repeat(count: 3))
        // modelEntity.playAnimation(animation.speed(1.5))
    }
    
    // Add the model to the anchor
    anchor.addChild(modelEntity)
}
```

### 4. Placing Models on Detected Surfaces

To allow users to tap and place models on detected surfaces:

```swift
// Add a tap gesture recognizer
let tapGesture = UITapGestureRecognizer(target: context.coordinator, action: #selector(Coordinator.handleTap))
arView.addGestureRecognizer(tapGesture)

// In your Coordinator class
@objc func handleTap(_ recognizer: UITapGestureRecognizer) {
    let location = recognizer.location(in: arView)
    
    // Raycast to find a surface
    let results = arView.raycast(from: location, allowing: .estimatedPlane, alignment: .horizontal)
    
    if let firstResult = results.first {
        // Create an anchor at the tap location
        let anchor = AnchorEntity(raycastResult: firstResult)
        
        // Load and add the model
        if let modelEntity = try? ModelEntity.load(named: "b2_animated") {
            // Scale the model if needed
            modelEntity.scale = SIMD3<Float>(0.1, 0.1, 0.1)
            
            // Add the model to the anchor
            anchor.addChild(modelEntity)
            
            // Add the anchor to the scene
            arView.scene.addAnchor(anchor)
        }
    }
}
```

## Troubleshooting

### Model Not Appearing

1. Make sure the USDZ file is properly added to your Xcode project and included in the target's "Copy Bundle Resources" build phase
2. Check that the model name in your code matches the filename (without extension)
3. Try adjusting the scale of the model - it might be too large or too small to be visible

### Animation Not Playing

1. Check if the model has animations using `modelEntity.availableAnimations`
2. If no animations are found, the USDZ file might not contain animation data
3. Try creating a new animated USDZ file with the provided script

### Performance Issues

1. Reduce the complexity of the model or animation
2. Lower the scale of the model
3. Use a device with better performance capabilities

## Additional Resources

- [Apple Developer Documentation: RealityKit](https://developer.apple.com/documentation/realitykit)
- [Apple Developer Documentation: ARKit](https://developer.apple.com/documentation/arkit)
- [USDZ File Format Specification](https://graphics.pixar.com/usd/docs/Usdz-File-Format-Specification.html)