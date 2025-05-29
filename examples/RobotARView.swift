import SwiftUI
import RealityKit
import ARKit

struct RobotARView: View {
    var body: some View {
        ZStack {
            ARViewContainer()
                .edgesIgnoringSafeArea(.all)
            
            VStack {
                Spacer()
                HStack {
                    Button(action: {
                        NotificationCenter.default.post(name: Notification.Name("LoadSimpleRobot"), object: nil)
                    }) {
                        Text("Simple Robot")
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        NotificationCenter.default.post(name: Notification.Name("LoadComplexRobot"), object: nil)
                    }) {
                        Text("Complex Robot")
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
            }
        }
    }
}

struct ARViewContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Configure AR session
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal]
        arView.session.run(configuration)
        
        // Set up notification observers
        context.coordinator.setupNotifications(arView: arView)
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject {
        var currentAnchor: AnchorEntity?
        
        func setupNotifications(arView: ARView) {
            NotificationCenter.default.addObserver(forName: Notification.Name("LoadSimpleRobot"), object: nil, queue: .main) { [weak self] _ in
                self?.loadModel(named: "animated_robot.usdz", in: arView)
            }
            
            NotificationCenter.default.addObserver(forName: Notification.Name("LoadComplexRobot"), object: nil, queue: .main) { [weak self] _ in
                self?.loadModel(named: "complex_robot.usdz", in: arView)
            }
        }
        
        func loadModel(named modelName: String, in arView: ARView) {
            // Remove existing model if any
            if let currentAnchor = currentAnchor {
                arView.scene.removeAnchor(currentAnchor)
                self.currentAnchor = nil
            }
            
            // Load the USDZ model
            do {
                let modelEntity = try ModelEntity.load(named: modelName)
                
                // Create an anchor for the model
                let anchor = AnchorEntity(plane: .horizontal)
                anchor.addChild(modelEntity)
                
                // Scale the model to a reasonable size
                modelEntity.scale = SIMD3<Float>(0.5, 0.5, 0.5)
                
                // Add the anchor to the scene
                arView.scene.addAnchor(anchor)
                self.currentAnchor = anchor
                
                // Play animation if available
                if let animation = modelEntity.availableAnimations.first {
                    modelEntity.playAnimation(animation.repeat())
                }
            } catch {
                print("Failed to load model: \(error.localizedDescription)")
            }
        }
    }
}

// Preview provider for SwiftUI canvas
struct RobotARView_Previews: PreviewProvider {
    static var previews: some View {
        RobotARView()
    }
}