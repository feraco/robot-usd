import SwiftUI
import RealityKit
import ARKit
import Combine

struct RobotARView: View {
    @State private var modelName: String = "b2_animated"
    @State private var modelScale: Float = 0.1
    
    var body: some View {
        ZStack {
            ARViewContainer(modelName: modelName, modelScale: modelScale)
                .edgesIgnoringSafeArea(.all)
            
            VStack {
                Spacer()
                
                HStack {
                    Button(action: {
                        modelName = "b2_animated"
                        modelScale = 0.1
                    }) {
                        Text("B2 Robot")
                            .padding()
                            .background(modelName == "b2_animated" ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        modelName = "g1_animated"
                        modelScale = 0.05
                    }) {
                        Text("G1 Robot")
                            .padding()
                            .background(modelName == "g1_animated" ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        modelName = "cf2x_animated"
                        modelScale = 1.0
                    }) {
                        Text("Crazyflie")
                            .padding()
                            .background(modelName == "cf2x_animated" ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        modelName = "custom_drone_example"
                        modelScale = 1.0
                    }) {
                        Text("Custom Drone")
                            .padding()
                            .background(modelName == "custom_drone_example" ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
                .background(Color.black.opacity(0.5))
                .cornerRadius(16)
                .padding()
            }
        }
    }
}

struct ARViewContainer: UIViewRepresentable {
    var modelName: String
    var modelScale: Float
    
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Configure AR session
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal]
        arView.session.run(config)
        
        // Add coaching overlay
        let coachingOverlay = ARCoachingOverlayView()
        coachingOverlay.session = arView.session
        coachingOverlay.goal = .horizontalPlane
        coachingOverlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        arView.addSubview(coachingOverlay)
        
        // Add tap gesture
        let tapGesture = UITapGestureRecognizer(target: context.coordinator, action: #selector(Coordinator.handleTap))
        arView.addGestureRecognizer(tapGesture)
        
        context.coordinator.arView = arView
        context.coordinator.modelName = modelName
        context.coordinator.modelScale = modelScale
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {
        context.coordinator.modelName = modelName
        context.coordinator.modelScale = modelScale
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(modelName: modelName, modelScale: modelScale)
    }
    
    class Coordinator: NSObject {
        var arView: ARView?
        var modelName: String
        var modelScale: Float
        var cancellables = Set<AnyCancellable>()
        
        init(modelName: String, modelScale: Float) {
            self.modelName = modelName
            self.modelScale = modelScale
            super.init()
        }
        
        @objc func handleTap(_ recognizer: UITapGestureRecognizer) {
            guard let arView = arView else { return }
            
            let location = recognizer.location(in: arView)
            
            // Raycast to find a surface
            let results = arView.raycast(from: location, allowing: .estimatedPlane, alignment: .horizontal)
            
            if let firstResult = results.first {
                // Create an anchor at the tap location
                let anchor = AnchorEntity(raycastResult: firstResult)
                
                // Load and add the model
                loadModel(anchor: anchor)
            }
        }
        
        func loadModel(anchor: AnchorEntity) {
            guard let arView = arView else { return }
            
            // Try to load the model
            do {
                let modelEntity = try ModelEntity.load(named: modelName)
                
                // Scale the model
                modelEntity.scale = SIMD3<Float>(modelScale, modelScale, modelScale)
                
                // Check for animations
                if let animation = modelEntity.availableAnimations.first {
                    // Play the animation in a loop
                    modelEntity.playAnimation(animation.repeat())
                }
                
                // Add the model to the anchor
                anchor.addChild(modelEntity)
                
                // Add the anchor to the scene
                arView.scene.addAnchor(anchor)
                
            } catch {
                print("Error loading model: \(error.localizedDescription)")
            }
        }
    }
}

struct RobotARView_Previews: PreviewProvider {
    static var previews: some View {
        RobotARView()
    }
}