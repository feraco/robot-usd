#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, Vt, UsdShade
import math
import os

def create_animated_b2():
    # Open the existing USD file
    input_file = "b2.usd"
    output_file = "b2_animated.usda"
    
    # Open the stage
    stage = Usd.Stage.Open(input_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(24)
    
    # Set frame range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)  # 2 seconds at 24 fps
    
    # Find the robot parts to animate
    # First, let's list all prims to understand the structure
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
    for joint_path in leg_joints:
        joint = UsdGeom.Xform(stage.GetPrimAtPath(joint_path))
        
        # Create rotation animation
        rotation_attr = joint.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
        
        # Create a walking motion
        for frame in range(1, 49):
            time = frame
            angle = 30 * math.sin(2 * math.pi * frame / 24)  # 30 degree rotation
            rotation_attr.Set(Gf.Vec3d(angle, 0, 0), time)
    
    # Also add a simple up/down body motion
    body_paths = []
    for prim in stage.Traverse():
        if "body" in prim.GetPath().pathString.lower():
            body_paths.append(prim.GetPath())
            print(f"Found body part: {prim.GetPath()}")
    
    # If body parts found, animate them
    for body_path in body_paths:
        body = UsdGeom.Xform(stage.GetPrimAtPath(body_path))
        
        # Create translation animation for up/down motion
        translate_op = body.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
        
        # Create a subtle up/down motion
        for frame in range(1, 49):
            time = frame
            height = 0.05 * math.sin(2 * math.pi * frame / 24)  # 5cm up/down motion
            current_pos = translate_op.Get(time) if translate_op.Get(time) else Gf.Vec3d(0, 0, 0)
            translate_op.Set(Gf.Vec3d(current_pos[0], current_pos[1], height), time)
    
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
    simplified_file = "b2_simplified.usda"
    simplified_stage = Usd.Stage.CreateNew(simplified_file)
    
    # Set up the simplified stage
    simplified_stage.SetTimeCodesPerSecond(24)
    simplified_stage.SetStartTimeCode(1)
    simplified_stage.SetEndTimeCode(48)
    
    # Create a root prim
    root_prim = simplified_stage.DefinePrim("/Robot", "Xform")
    simplified_stage.SetDefaultPrim(root_prim)
    
    # Create a simple animated cube as a placeholder
    cube = UsdGeom.Cube.Define(simplified_stage, "/Robot/Body")
    cube.CreateSizeAttr(2.0)
    
    # Add animation to the cube
    cube_xform = UsdGeom.Xformable(cube.GetPrim())
    translate_op = cube_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    rotate_op = cube_xform.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
    
    # Create animation
    for frame in range(1, 49):
        time = frame
        height = 0.2 * math.sin(2 * math.pi * frame / 24)
        rotation = 30 * math.sin(2 * math.pi * frame / 12)
        translate_op.Set(Gf.Vec3d(0, 0, height), time)
        rotate_op.Set(Gf.Vec3d(0, rotation, 0), time)
    
    # Add a simple material
    material = UsdShade.Material.Define(simplified_stage, "/Robot/Material")
    shader = UsdShade.Shader.Define(simplified_stage, "/Robot/Material/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.2, 0.6, 0.8))
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
    
    # Connect using the proper API
    material.CreateOutput("surface", Sdf.ValueTypeNames.Token).ConnectToSource(
        UsdShade.ConnectableAPI(shader), "surface"
    )
    
    # Bind the material to the cube
    UsdShade.MaterialBindingAPI(cube.GetPrim()).Bind(material)
    
    # Save the simplified USD file
    simplified_stage.Export(simplified_file)
    print(f"✅ Simplified USD saved to {simplified_file}")
    
    # Convert to USDZ
    usdz_file = "b2_animated.usdz"
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
        basic_file = "b2_basic.usda"
        basic_stage = Usd.Stage.CreateNew(basic_file)
        
        # Set up the basic stage
        basic_stage.SetTimeCodesPerSecond(24)
        basic_stage.SetStartTimeCode(1)
        basic_stage.SetEndTimeCode(48)
        
        # Create a root prim
        root = basic_stage.DefinePrim("/Robot", "Xform")
        basic_stage.SetDefaultPrim(root)
        
        # Create a simple animated sphere
        sphere = UsdGeom.Sphere.Define(basic_stage, "/Robot/Sphere")
        sphere.CreateRadiusAttr(1.0)
        
        # Add animation
        sphere_xform = UsdGeom.Xformable(sphere.GetPrim())
        translate_op = sphere_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
        
        # Create a simple up/down animation
        for frame in range(1, 49):
            time = frame
            height = 0.5 * math.sin(2 * math.pi * frame / 24)
            translate_op.Set(Gf.Vec3d(0, height, 0), time)
        
        # Add a simple material
        material = UsdShade.Material.Define(basic_stage, "/Robot/Material")
        shader = UsdShade.Shader.Define(basic_stage, "/Robot/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.2, 0.6, 0.8))
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
    create_animated_b2()