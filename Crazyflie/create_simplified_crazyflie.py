#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, Vt
import math
import os

def create_simplified_crazyflie():
    # Output files
    output_file = "cf2x_simplified.usda"
    usdz_file = "cf2x_simplified.usdz"
    
    # Create a new stage
    stage = Usd.Stage.CreateNew(output_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(24)
    
    # Set frame range - 2 seconds at 24 fps
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)
    
    # Create a root prim
    root = UsdGeom.Xform.Define(stage, "/crazyflie")
    stage.SetDefaultPrim(root.GetPrim())
    
    # Create the drone body
    body = UsdGeom.Xform.Define(stage, "/crazyflie/body")
    
    # Create the main body as a cube
    main_body = UsdGeom.Cube.Define(stage, "/crazyflie/body/main")
    main_body.CreateSizeAttr(0.03)  # 3cm cube
    main_body_xform = UsdGeom.Xformable(main_body.GetPrim())
    main_body_xform.AddScaleOp().Set(Gf.Vec3d(1.0, 0.2, 1.0))  # Flatten it
    
    # Create circuit board as a thin disk
    circuit = UsdGeom.Cylinder.Define(stage, "/crazyflie/body/circuit")
    circuit.CreateRadiusAttr(0.015)  # 1.5cm radius
    circuit.CreateHeightAttr(0.002)  # 2mm height
    circuit_xform = UsdGeom.Xformable(circuit.GetPrim())
    circuit_xform.AddTranslateOp().Set(Gf.Vec3d(0, 0.004, 0))  # Position on top of body
    
    # Create battery as a small box
    battery = UsdGeom.Cube.Define(stage, "/crazyflie/body/battery")
    battery.CreateSizeAttr(0.01)  # 1cm cube
    battery_xform = UsdGeom.Xformable(battery.GetPrim())
    battery_xform.AddScaleOp().Set(Gf.Vec3d(1.5, 0.5, 1.0))  # Shape it
    battery_xform.AddTranslateOp().Set(Gf.Vec3d(0, -0.005, 0))  # Position under body
    
    # Create four motor arms
    arm_positions = [
        (0.015, 0, 0.015),  # Front right
        (-0.015, 0, 0.015),  # Front left
        (-0.015, 0, -0.015),  # Back left
        (0.015, 0, -0.015)   # Back right
    ]
    
    for i, (x, y, z) in enumerate(arm_positions):
        # Create arm
        arm = UsdGeom.Cylinder.Define(stage, f"/crazyflie/body/arm_{i+1}")
        arm.CreateRadiusAttr(0.002)  # 2mm radius
        arm.CreateHeightAttr(0.02)  # 2cm length
        arm_xform = UsdGeom.Xformable(arm.GetPrim())
        
        # Position and rotate arm
        angle = math.atan2(z, x) * 180 / math.pi
        # Combine rotations into a single operation
        arm_xform.AddRotateXYZOp().Set(Gf.Vec3d(0, angle, 90))  # Make horizontal and point in right direction
        arm_xform.AddTranslateOp().Set(Gf.Vec3d(x/2, y, z/2))  # Position
        
        # Create motor
        motor = UsdGeom.Cylinder.Define(stage, f"/crazyflie/body/motor_{i+1}")
        motor.CreateRadiusAttr(0.004)  # 4mm radius
        motor.CreateHeightAttr(0.004)  # 4mm height
        motor_xform = UsdGeom.Xformable(motor.GetPrim())
        motor_xform.AddTranslateOp().Set(Gf.Vec3d(x, y, z))  # Position at end of arm
        
        # Create propeller joint
        prop_joint = UsdGeom.Xform.Define(stage, f"/crazyflie/body/prop_joint_{i+1}")
        prop_joint_xform = UsdGeom.Xformable(prop_joint.GetPrim())
        prop_joint_xform.AddTranslateOp().Set(Gf.Vec3d(x, y + 0.002, z))  # Position above motor
        
        # Create propeller
        prop = UsdGeom.Cylinder.Define(stage, f"/crazyflie/prop_{i+1}")
        prop.CreateRadiusAttr(0.012)  # 1.2cm radius
        prop.CreateHeightAttr(0.001)  # 1mm height
        prop_xform = UsdGeom.Xformable(prop.GetPrim())
        prop_xform.AddTranslateOp().Set(Gf.Vec3d(x, y + 0.003, z))  # Position above joint
        
        # Add rotation animation to propeller
        # Alternate direction: odd-numbered props CCW, even-numbered CW
        direction = -1 if i % 2 == 0 else 1
        rotate_op = prop_xform.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
        
        # Create a continuous rotation animation
        for frame in range(1, 49):
            time = frame
            angle = direction * (720 / 24) * frame  # 720 degrees per second (2 rotations)
            rotate_op.Set(Gf.Vec3d(0, angle, 0), time)
    
    # Add a subtle hovering motion to the entire drone
    hover_op = root.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    
    # Create a subtle up/down hovering motion
    for frame in range(1, 49):
        time = frame
        height = 0.005 * math.sin(2 * math.pi * frame / 24)  # 5mm up/down motion
        hover_op.Set(Gf.Vec3d(0, height, 0), time)
    
    # Define colors for different parts
    colors = {
        # Main body - black
        "/crazyflie/body/main": Gf.Vec3f(0.1, 0.1, 0.1),
        
        # Circuit board - green
        "/crazyflie/body/circuit": Gf.Vec3f(0.0, 0.5, 0.0),
        
        # Battery - silver
        "/crazyflie/body/battery": Gf.Vec3f(0.8, 0.8, 0.8),
        
        # Arms - dark gray
        "/crazyflie/body/arm_1": Gf.Vec3f(0.3, 0.3, 0.3),
        "/crazyflie/body/arm_2": Gf.Vec3f(0.3, 0.3, 0.3),
        "/crazyflie/body/arm_3": Gf.Vec3f(0.3, 0.3, 0.3),
        "/crazyflie/body/arm_4": Gf.Vec3f(0.3, 0.3, 0.3),
        
        # Motors - dark gray
        "/crazyflie/body/motor_1": Gf.Vec3f(0.25, 0.25, 0.25),
        "/crazyflie/body/motor_2": Gf.Vec3f(0.25, 0.25, 0.25),
        "/crazyflie/body/motor_3": Gf.Vec3f(0.25, 0.25, 0.25),
        "/crazyflie/body/motor_4": Gf.Vec3f(0.25, 0.25, 0.25),
        
        # Propellers - alternating red and blue
        "/crazyflie/prop_1": Gf.Vec3f(0.8, 0.0, 0.0),  # Red
        "/crazyflie/prop_2": Gf.Vec3f(0.0, 0.0, 0.8),  # Blue
        "/crazyflie/prop_3": Gf.Vec3f(0.8, 0.0, 0.0),  # Red
        "/crazyflie/prop_4": Gf.Vec3f(0.0, 0.0, 0.8)   # Blue
    }
    
    # Apply colors to parts
    for part_path, color in colors.items():
        # Create a new material for this part
        material_path = part_path.replace("/", "_") + "_material"
        material = UsdShade.Material.Define(stage, "/Materials" + material_path)
        
        # Create a PBR shader
        shader = UsdShade.Shader.Define(stage, "/Materials" + material_path + "/shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Set color and other properties
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        
        # Connect shader to material
        material.CreateOutput("surface", Sdf.ValueTypeNames.Token).ConnectToSource(
            UsdShade.ConnectableAPI(shader), "surface"
        )
        
        # Bind material to part
        UsdShade.MaterialBindingAPI(stage.GetPrimAtPath(part_path)).Bind(material)
        
        print(f"Applied color to {part_path}")
    
    # Save the animated USD file
    stage.Export(output_file)
    print(f"✅ Simplified animated USD saved to {output_file}")
    
    # Convert to USDZ
    try:
        UsdUtils.CreateNewUsdzPackage(
            Sdf.AssetPath(output_file),
            usdz_file
        )
        print(f"✅ USDZ package created at {usdz_file}")
    except Exception as e:
        print(f"❌ Error creating USDZ package: {e}")

if __name__ == "__main__":
    create_simplified_crazyflie()