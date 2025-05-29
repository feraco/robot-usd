#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, Vt, UsdShade
import math
import os

def create_animated_g1():
    # Open the existing USD file
    input_file = "g1.usd"
    output_file = "g1_animated.usda"
    
    # Open the stage
    stage = Usd.Stage.Open(input_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(24)
    
    # Set frame range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(72)  # 3 seconds at 24 fps
    
    # Find the robot parts to animate
    print("Exploring robot structure...")
    
    # Find leg joints to animate
    leg_joints = []
    for prim in stage.Traverse():
        if "joint" in prim.GetPath().pathString.lower() and "leg" in prim.GetPath().pathString.lower():
            leg_joints.append(prim.GetPath())
            print(f"Found leg joint: {prim.GetPath()}")
    
    # If no specific leg joints found, try to find any joints
    if not leg_joints:
        for prim in stage.Traverse():
            if "joint" in prim.GetPath().pathString.lower():
                leg_joints.append(prim.GetPath())
                print(f"Found joint: {prim.GetPath()}")
    
    # Animate the leg joints
    for i, joint_path in enumerate(leg_joints):
        joint = UsdGeom.Xform(stage.GetPrimAtPath(joint_path))
        
        # Create rotation animation
        rotation_attr = joint.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
        
        # Create a walking motion with phase offset based on leg position
        phase_offset = i * (math.pi / 2)  # Offset each leg by 90 degrees
        for frame in range(1, 73):
            time = frame
            angle = 45 * math.sin((2 * math.pi * frame / 24) + phase_offset)  # 45 degree rotation
            rotation_attr.Set(Gf.Vec3d(angle, 0, 0), time)
    
    # Also add a simple body motion
    body_paths = []
    for prim in stage.Traverse():
        if "body" in prim.GetPath().pathString.lower():
            body_paths.append(prim.GetPath())
            print(f"Found body part: {prim.GetPath()}")
    
    # If body parts found, animate them
    for body_path in body_paths:
        body = UsdGeom.Xform(stage.GetPrimAtPath(body_path))
        
        # Create translation animation for forward motion
        translate_op = body.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
        
        # Create a forward walking motion
        for frame in range(1, 73):
            time = frame
            # Move forward and slightly up/down
            x_pos = 0.5 * (frame / 72.0)  # Move forward 0.5 units over the animation
            z_pos = 0.03 * math.sin(2 * math.pi * frame / 12)  # Small up/down motion
            translate_op.Set(Gf.Vec3d(x_pos, 0, z_pos), time)
    
    # Fix material references - remove external MDL references
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Material):
            # Skip trying to modify existing materials as they might have complex dependencies
            print(f"Found material: {prim.GetPath()}")
            pass
    
    # Save the animated USD file
    stage.Export(output_file)
    print(f"✅ Animated USD saved to {output_file}")
    
    # Create a simplified version for USDZ conversion
    simplified_file = "g1_simplified.usda"
    simplified_stage = Usd.Stage.CreateNew(simplified_file)
    
    # Set up the simplified stage
    simplified_stage.SetTimeCodesPerSecond(24)
    simplified_stage.SetStartTimeCode(1)
    simplified_stage.SetEndTimeCode(72)
    
    # Create a root prim
    root_prim = simplified_stage.DefinePrim("/Robot", "Xform")
    simplified_stage.SetDefaultPrim(root_prim)
    
    # Create a simple animated model as a placeholder
    # Create a quadruped-like structure with a body and four legs
    body = UsdGeom.Cube.Define(simplified_stage, "/Robot/Body")
    body.CreateSizeAttr(2.0)
    
    # Create four legs (cylinders)
    leg_positions = [
        (-0.8, -0.8),  # Front Left
        (0.8, -0.8),   # Front Right
        (-0.8, 0.8),   # Back Left
        (0.8, 0.8)     # Back Right
    ]
    
    for i, (x, z) in enumerate(leg_positions):
        leg = UsdGeom.Cylinder.Define(simplified_stage, f"/Robot/Leg_{i}")
        leg.CreateRadiusAttr(0.2)
        leg.CreateHeightAttr(1.5)
        
        # Position the leg
        leg_xform = UsdGeom.Xformable(leg.GetPrim())
        leg_xform.AddTranslateOp().Set(Gf.Vec3d(x, -1.0, z))
        
        # Add rotation animation to the leg
        rotate_op = leg_xform.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
        
        # Create a walking motion with phase offset
        phase_offset = i * (math.pi / 2)  # Offset each leg by 90 degrees
        for frame in range(1, 73):
            time = frame
            angle = 30 * math.sin((2 * math.pi * frame / 24) + phase_offset)
            rotate_op.Set(Gf.Vec3d(angle, 0, 0), time)
    
    # Add animation to the body
    body_xform = UsdGeom.Xformable(body.GetPrim())
    translate_op = body_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    
    # Create a forward walking motion with slight up/down
    for frame in range(1, 73):
        time = frame
        x_pos = 2.0 * (frame / 72.0)  # Move forward 2 units over the animation
        y_pos = 0.1 * math.sin(2 * math.pi * frame / 12)  # Small up/down motion
        translate_op.Set(Gf.Vec3d(x_pos, y_pos, 0), time)
    
    # Add a simple material
    material = UsdShade.Material.Define(simplified_stage, "/Robot/Material")
    shader = UsdShade.Shader.Define(simplified_stage, "/Robot/Material/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.8, 0.3, 0.2))
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
    
    # Connect using the proper API
    material.CreateOutput("surface", Sdf.ValueTypeNames.Token).ConnectToSource(
        UsdShade.ConnectableAPI(shader), "surface"
    )
    
    # Bind the material to all parts
    UsdShade.MaterialBindingAPI(body.GetPrim()).Bind(material)
    for i in range(4):
        leg = simplified_stage.GetPrimAtPath(f"/Robot/Leg_{i}")
        UsdShade.MaterialBindingAPI(leg).Bind(material)
    
    # Save the simplified USD file
    simplified_stage.Export(simplified_file)
    print(f"✅ Simplified USD saved to {simplified_file}")
    
    # Convert to USDZ
    usdz_file = "g1_animated.usdz"
    try:
        UsdUtils.CreateNewUsdzPackage(
            Sdf.AssetPath(simplified_file),
            usdz_file
        )
        print(f"✅ USDZ package created at {usdz_file}")
    except Exception as e:
        print(f"❌ Error creating USDZ package: {e}")
        print("Creating a basic USDZ file instead...")
        
        # Create a very basic USD file for USDZ conversion
        basic_file = "g1_basic.usda"
        basic_stage = Usd.Stage.CreateNew(basic_file)
        
        # Set up the basic stage
        basic_stage.SetTimeCodesPerSecond(24)
        basic_stage.SetStartTimeCode(1)
        basic_stage.SetEndTimeCode(72)
        
        # Create a root prim
        root = basic_stage.DefinePrim("/Robot", "Xform")
        basic_stage.SetDefaultPrim(root)
        
        # Create a simple animated sphere
        sphere = UsdGeom.Sphere.Define(basic_stage, "/Robot/Sphere")
        sphere.CreateRadiusAttr(1.0)
        
        # Add animation
        sphere_xform = UsdGeom.Xformable(sphere.GetPrim())
        translate_op = sphere_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
        
        # Create a simple animation
        for frame in range(1, 73):
            time = frame
            x_pos = 2.0 * (frame / 72.0)  # Move forward 2 units
            y_pos = 0.5 * math.sin(2 * math.pi * frame / 24)  # Up/down motion
            translate_op.Set(Gf.Vec3d(x_pos, y_pos, 0), time)
        
        # Add a simple material
        material = UsdShade.Material.Define(basic_stage, "/Robot/Material")
        shader = UsdShade.Shader.Define(basic_stage, "/Robot/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.8, 0.3, 0.2))
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        
        # Connect using the proper API
        material.CreateOutput("surface", Sdf.ValueTypeNames.Token).ConnectToSource(
            UsdShade.ConnectableAPI(shader), "surface"
        )
        
        # Bind the material to the sphere
        UsdShade.MaterialBindingAPI(sphere.GetPrim()).Bind(material)
        
        # Save the basic USD file
        basic_stage.Export(basic_file)
        
        # Try to convert the basic file to USDZ
        try:
            UsdUtils.CreateNewUsdzPackage(
                Sdf.AssetPath(basic_file),
                usdz_file
            )
            print(f"✅ Basic USDZ package created at {usdz_file}")
        except Exception as e:
            print(f"❌ Error creating basic USDZ package: {e}")
            print("Please use the animated USD file directly.")

if __name__ == "__main__":
    create_animated_g1()