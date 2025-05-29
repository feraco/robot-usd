#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, Vt
import math
import os

def create_animated_crazyflie():
    # Input and output files
    input_file = "cf2x.usd"
    output_file = "cf2x_animated_color.usda"
    usdz_file = "cf2x_animated_color.usdz"
    
    # Open the stage
    stage = Usd.Stage.Open(input_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(24)
    
    # Set frame range - 2 seconds at 24 fps
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)
    
    # Set default prim
    stage.SetDefaultPrim(stage.GetPrimAtPath("/crazyflie"))
    
    print("Exploring Crazyflie structure...")
    
    # Find propellers to animate
    propellers = [
        "/crazyflie/m1_prop",
        "/crazyflie/m2_prop",
        "/crazyflie/m3_prop",
        "/crazyflie/m4_prop"
    ]
    
    # Define rotation speeds and directions for each propeller
    # CCW propellers: m1 and m3, CW propellers: m2 and m4
    rotation_speeds = {
        "/crazyflie/m1_prop": -720,  # CCW, 2 full rotations per second
        "/crazyflie/m2_prop": 720,   # CW, 2 full rotations per second
        "/crazyflie/m3_prop": -720,  # CCW, 2 full rotations per second
        "/crazyflie/m4_prop": 720    # CW, 2 full rotations per second
    }
    
    # Animate the propellers
    for prop_path in propellers:
        prop = UsdGeom.Xform(stage.GetPrimAtPath(prop_path))
        
        # Create rotation animation
        rotation_attr = prop.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
        
        # Get rotation speed and direction
        speed = rotation_speeds[prop_path]
        
        # Create a continuous rotation animation
        for frame in range(1, 49):
            time = frame
            angle = (speed / 24) * frame  # Degrees per frame
            rotation_attr.Set(Gf.Vec3d(0, 0, angle), time)
        
        print(f"Added rotation animation to {prop_path}")
    
    # Add a subtle hovering motion to the entire drone
    drone = UsdGeom.Xform(stage.GetPrimAtPath("/crazyflie"))
    translate_op = drone.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    
    # Create a subtle up/down hovering motion
    for frame in range(1, 49):
        time = frame
        height = 0.005 * math.sin(2 * math.pi * frame / 24)  # 5mm up/down motion
        translate_op.Set(Gf.Vec3d(0, height, 0), time)
    
    print("Added hovering animation to drone body")
    
    # Define colors for different parts
    colors = {
        # Main body - black
        "/crazyflie/body/body_visual/cf_body_001": Gf.Vec3f(0.1, 0.1, 0.1),
        
        # Circuit board - green
        "/crazyflie/body/body_visual/Cylinder": Gf.Vec3f(0.0, 0.5, 0.0),
        
        # Battery - silver
        "/crazyflie/body/body_visual/battery": Gf.Vec3f(0.8, 0.8, 0.8),
        
        # Battery holder - dark gray
        "/crazyflie/body/body_visual/battery_holder": Gf.Vec3f(0.3, 0.3, 0.3),
        
        # Pin headers - gold
        "/crazyflie/body/body_visual/pin_headers": Gf.Vec3f(0.85, 0.65, 0.13),
        
        # Motor mounts - dark gray
        "/crazyflie/body/body_visual/motor_mount": Gf.Vec3f(0.25, 0.25, 0.25),
        
        # CCW Propellers - red
        "/crazyflie/m1_prop/ccw_prop": Gf.Vec3f(0.8, 0.0, 0.0),
        "/crazyflie/m3_prop/ccw_prop": Gf.Vec3f(0.8, 0.0, 0.0),
        
        # CW Propellers - blue
        "/crazyflie/m2_prop/cw_prop": Gf.Vec3f(0.0, 0.0, 0.8),
        "/crazyflie/m4_prop/cw_prop": Gf.Vec3f(0.0, 0.0, 0.8)
    }
    
    # Apply colors to parts
    for part_path, color in colors.items():
        if stage.GetPrimAtPath(part_path):
            # Create a new material for this part
            material_path = part_path + "_material"
            material = UsdShade.Material.Define(stage, material_path)
            
            # Create a PBR shader
            shader = UsdShade.Shader.Define(stage, material_path + "/shader")
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
    print(f"✅ Animated USD saved to {output_file}")
    
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
    create_animated_crazyflie()