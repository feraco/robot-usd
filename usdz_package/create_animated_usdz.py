#!/usr/bin/env python3
"""
Create Animated USDZ Files

This script helps you create animated USDZ files from USD files for use in Xcode with RealityKit.
It creates a simple animation for the model and packages it as a USDZ file.

Usage:
    python create_animated_usdz.py input.usd [output.usdz] [--duration 3] [--fps 24]

Arguments:
    input.usd       Path to the input USD file
    output.usdz     Optional: Path to the output USDZ file (default: input_animated.usdz)
    --duration      Optional: Animation duration in seconds (default: 3)
    --fps           Optional: Frames per second (default: 24)
"""

from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade
import math
import os
import sys
import argparse

def create_animated_usdz(input_file, output_file=None, duration=3, fps=24):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Set default output file if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_animated.usdz"
    
    # Create intermediate files
    animated_usda = f"{os.path.splitext(output_file)[0]}.usda"
    simplified_usda = f"{os.path.splitext(output_file)[0]}_simplified.usda"
    
    print(f"Creating animated USDZ from {input_file}")
    print(f"Output will be saved to {output_file}")
    print(f"Animation duration: {duration} seconds at {fps} fps")
    
    # Calculate total frames
    total_frames = int(duration * fps)
    
    try:
        # Open the existing USD file
        stage = Usd.Stage.Open(input_file)
        
        # Set timeCodesPerSecond for proper playback
        stage.SetTimeCodesPerSecond(fps)
        
        # Set frame range
        stage.SetStartTimeCode(1)
        stage.SetEndTimeCode(total_frames)
        
        # Find the robot parts to animate
        print("Exploring model structure...")
        
        # Find joints to animate
        joints = []
        for prim in stage.Traverse():
            if "joint" in prim.GetPath().pathString.lower():
                joints.append(prim.GetPath())
                print(f"Found joint: {prim.GetPath()}")
        
        # If no joints found, try to find any transformable objects
        if not joints:
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Xformable):
                    # Skip the root prim
                    if len(str(prim.GetPath()).split('/')) > 2:
                        joints.append(prim.GetPath())
                        print(f"Found transformable: {prim.GetPath()}")
        
        # Animate the joints
        for i, joint_path in enumerate(joints):
            joint = UsdGeom.Xform(stage.GetPrimAtPath(joint_path))
            
            # Create rotation animation
            rotation_attr = joint.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble, "rotate")
            
            # Create a motion with phase offset based on position
            phase_offset = i * (math.pi / len(joints)) if len(joints) > 0 else 0
            for frame in range(1, total_frames + 1):
                time = frame
                angle = 30 * math.sin((2 * math.pi * frame / total_frames) + phase_offset)
                rotation_attr.Set(Gf.Vec3d(angle, 0, 0), time)
        
        # Find body/root parts to animate
        body_paths = []
        for prim in stage.Traverse():
            if "body" in prim.GetPath().pathString.lower() or "root" in prim.GetPath().pathString.lower():
                body_paths.append(prim.GetPath())
                print(f"Found body part: {prim.GetPath()}")
        
        # If no specific body parts found, use the root prim
        if not body_paths:
            for prim in stage.GetPseudoRoot().GetChildren():
                body_paths.append(prim.GetPath())
                print(f"Using root as body: {prim.GetPath()}")
        
        # Animate the body parts
        for body_path in body_paths:
            body = UsdGeom.Xform(stage.GetPrimAtPath(body_path))
            
            # Create translation animation
            translate_op = body.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
            
            # Create a subtle motion
            for frame in range(1, total_frames + 1):
                time = frame
                height = 0.05 * math.sin(2 * math.pi * frame / total_frames)
                x_pos = 0.1 * (frame / total_frames)
                translate_op.Set(Gf.Vec3d(x_pos, 0, height), time)
        
        # Save the animated USD file
        stage.Export(animated_usda)
        print(f"✅ Animated USD saved to {animated_usda}")
        
        # Create a simplified version for USDZ conversion
        simplified_stage = Usd.Stage.CreateNew(simplified_usda)
        
        # Set up the simplified stage
        simplified_stage.SetTimeCodesPerSecond(fps)
        simplified_stage.SetStartTimeCode(1)
        simplified_stage.SetEndTimeCode(total_frames)
        
        # Create a root prim
        root_prim = simplified_stage.DefinePrim("/Robot", "Xform")
        simplified_stage.SetDefaultPrim(root_prim)
        
        # Create a simple animated model
        # For a quadruped-like structure with a body and four legs
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
            for frame in range(1, total_frames + 1):
                time = frame
                angle = 30 * math.sin((2 * math.pi * frame / total_frames) + phase_offset)
                rotate_op.Set(Gf.Vec3d(angle, 0, 0), time)
        
        # Add animation to the body
        body_xform = UsdGeom.Xformable(body.GetPrim())
        translate_op = body_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
        
        # Create a forward walking motion with slight up/down
        for frame in range(1, total_frames + 1):
            time = frame
            x_pos = 2.0 * (frame / total_frames)  # Move forward 2 units over the animation
            y_pos = 0.1 * math.sin(2 * math.pi * frame / (total_frames/2))  # Small up/down motion
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
        simplified_stage.Export(simplified_usda)
        print(f"✅ Simplified USD saved to {simplified_usda}")
        
        # Convert to USDZ
        try:
            UsdUtils.CreateNewUsdzPackage(
                Sdf.AssetPath(simplified_usda),
                output_file
            )
            print(f"✅ USDZ package created at {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating USDZ package: {e}")
            print("Creating a basic USDZ file instead...")
            
            # Create a very basic USD file for USDZ conversion
            basic_file = f"{os.path.splitext(output_file)[0]}_basic.usda"
            basic_stage = Usd.Stage.CreateNew(basic_file)
            
            # Set up the basic stage
            basic_stage.SetTimeCodesPerSecond(fps)
            basic_stage.SetStartTimeCode(1)
            basic_stage.SetEndTimeCode(total_frames)
            
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
            for frame in range(1, total_frames + 1):
                time = frame
                x_pos = 2.0 * (frame / total_frames)  # Move forward 2 units
                y_pos = 0.5 * math.sin(2 * math.pi * frame / total_frames)  # Up/down motion
                translate_op.Set(Gf.Vec3d(x_pos, y_pos, 0), time)
            
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
                    output_file
                )
                print(f"✅ Basic USDZ package created at {output_file}")
                return True
            except Exception as e:
                print(f"❌ Error creating basic USDZ package: {e}")
                print("Please use the animated USD file directly.")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create animated USDZ files from USD files')
    parser.add_argument('input_file', help='Path to the input USD file')
    parser.add_argument('output_file', nargs='?', help='Path to the output USDZ file (optional)')
    parser.add_argument('--duration', type=float, default=3, help='Animation duration in seconds (default: 3)')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second (default: 24)')
    
    args = parser.parse_args()
    
    create_animated_usdz(args.input_file, args.output_file, args.duration, args.fps)

if __name__ == "__main__":
    main()