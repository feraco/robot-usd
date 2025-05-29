#!/usr/bin/env python3
"""
Create Animated Drone USDZ

This script creates an animated drone USDZ file with spinning propellers.
You can customize the colors and dimensions of the drone.

Usage:
    python create_drone.py [output.usdz] [--duration 3] [--fps 24] [--body-color 0.1,0.1,0.1] [--prop1-color 0.8,0.0,0.0] [--prop2-color 0.0,0.0,0.8]

Arguments:
    output.usdz     Optional: Path to the output USDZ file (default: drone_animated.usdz)
    --duration      Optional: Animation duration in seconds (default: 3)
    --fps           Optional: Frames per second (default: 24)
    --body-color    Optional: RGB color for the drone body (default: 0.1,0.1,0.1)
    --prop1-color   Optional: RGB color for propellers 1 and 3 (default: 0.8,0.0,0.0)
    --prop2-color   Optional: RGB color for propellers 2 and 4 (default: 0.0,0.0,0.8)
"""

from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, UsdLux
import math
import os
import sys
import argparse

def parse_color(color_str):
    """Parse a comma-separated RGB color string into a Gf.Vec3f"""
    try:
        r, g, b = map(float, color_str.split(','))
        return Gf.Vec3f(r, g, b)
    except:
        print(f"Error parsing color '{color_str}'. Using default.")
        return None

def create_animated_drone(output_file=None, duration=3, fps=24, 
                         body_color=Gf.Vec3f(0.1, 0.1, 0.1),
                         prop1_color=Gf.Vec3f(0.8, 0.0, 0.0),
                         prop2_color=Gf.Vec3f(0.0, 0.0, 0.8)):
    # Set default output file if not provided
    if output_file is None:
        output_file = "drone_animated.usdz"
    
    # Create intermediate file
    usda_file = f"{os.path.splitext(output_file)[0]}.usda"
    
    print(f"Creating animated drone USDZ")
    print(f"Output will be saved to {output_file}")
    print(f"Animation duration: {duration} seconds at {fps} fps")
    
    # Calculate total frames
    total_frames = int(duration * fps)
    
    # Create a new stage
    stage = Usd.Stage.CreateNew(usda_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(fps)
    
    # Set frame range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(total_frames)
    
    # Create a root prim
    root = UsdGeom.Xform.Define(stage, "/drone")
    stage.SetDefaultPrim(root.GetPrim())
    
    # Create the drone body
    body = UsdGeom.Xform.Define(stage, "/drone/body")
    
    # Create the main body as a cube
    main_body = UsdGeom.Cube.Define(stage, "/drone/body/main")
    main_body.CreateSizeAttr(1.0)  # 1 unit cube
    main_body_xform = UsdGeom.Xformable(main_body.GetPrim())
    main_body_xform.AddScaleOp().Set(Gf.Vec3d(3.0, 0.5, 3.0))  # Flatten it and make it wider
    
    # Create circuit board as a thin disk
    circuit = UsdGeom.Cylinder.Define(stage, "/drone/body/circuit")
    circuit.CreateRadiusAttr(1.4)  # Radius
    circuit.CreateHeightAttr(0.1)  # Height
    circuit_xform = UsdGeom.Xformable(circuit.GetPrim())
    circuit_xform.AddTranslateOp().Set(Gf.Vec3d(0, 0.3, 0))  # Position on top of body
    
    # Create battery as a box
    battery = UsdGeom.Cube.Define(stage, "/drone/body/battery")
    battery.CreateSizeAttr(1.0)  # 1 unit cube
    battery_xform = UsdGeom.Xformable(battery.GetPrim())
    battery_xform.AddScaleOp().Set(Gf.Vec3d(1.5, 0.3, 1.0))  # Shape it
    battery_xform.AddTranslateOp().Set(Gf.Vec3d(0, -0.3, 0))  # Position under body
    
    # Create four motor arms
    arm_positions = [
        (1.5, 0, 1.5),   # Front right
        (-1.5, 0, 1.5),  # Front left
        (-1.5, 0, -1.5), # Back left
        (1.5, 0, -1.5)   # Back right
    ]
    
    for i, (x, y, z) in enumerate(arm_positions):
        # Create arm
        arm = UsdGeom.Cylinder.Define(stage, f"/drone/body/arm_{i+1}")
        arm.CreateRadiusAttr(0.1)  # Radius
        arm.CreateHeightAttr(2.0)  # Length
        arm_xform = UsdGeom.Xformable(arm.GetPrim())
        
        # Calculate angle to point arm in right direction
        angle = math.degrees(math.atan2(z, x))
        
        # Position and rotate arm
        # First make it horizontal (rotate around Z)
        arm_xform.AddRotateZOp().Set(90)
        # Then rotate around Y to point in right direction
        arm_xform.AddRotateYOp().Set(angle)
        # Position at half distance from center
        arm_xform.AddTranslateOp().Set(Gf.Vec3d(x/2, y, z/2))
        
        # Create motor
        motor = UsdGeom.Cylinder.Define(stage, f"/drone/body/motor_{i+1}")
        motor.CreateRadiusAttr(0.3)  # Radius
        motor.CreateHeightAttr(0.3)  # Height
        motor_xform = UsdGeom.Xformable(motor.GetPrim())
        motor_xform.AddTranslateOp().Set(Gf.Vec3d(x, y, z))  # Position at end of arm
        
        # Create propeller
        prop = UsdGeom.Cylinder.Define(stage, f"/drone/prop_{i+1}")
        prop.CreateRadiusAttr(0.8)  # Radius
        prop.CreateHeightAttr(0.05)  # Height
        prop_xform = UsdGeom.Xformable(prop.GetPrim())
        prop_xform.AddTranslateOp().Set(Gf.Vec3d(x, y + 0.2, z))  # Position above motor
        
        # Add rotation animation to propeller
        # Alternate direction: odd-numbered props CCW, even-numbered CW
        direction = -1 if i % 2 == 0 else 1
        rotate_op = prop_xform.AddRotateYOp(UsdGeom.XformOp.PrecisionDouble, "rotateY")
        
        # Create a continuous rotation animation
        for frame in range(1, total_frames + 1):
            time = frame
            angle = direction * (720 / fps) * frame  # 720 degrees per second (2 rotations)
            rotate_op.Set(angle, time)
    
    # Add a subtle hovering motion to the entire drone
    hover_op = root.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    
    # Create a subtle up/down hovering motion
    for frame in range(1, total_frames + 1):
        time = frame
        height = 0.2 * math.sin(2 * math.pi * frame / total_frames)  # Up/down motion
        hover_op.Set(Gf.Vec3d(0, height, 0), time)
    
    # Define colors for different parts
    colors = {
        # Main body - user defined
        "/drone/body/main": body_color,
        
        # Circuit board - green
        "/drone/body/circuit": Gf.Vec3f(0.0, 0.5, 0.0),
        
        # Battery - silver
        "/drone/body/battery": Gf.Vec3f(0.8, 0.8, 0.8),
        
        # Arms - dark gray
        "/drone/body/arm_1": Gf.Vec3f(0.3, 0.3, 0.3),
        "/drone/body/arm_2": Gf.Vec3f(0.3, 0.3, 0.3),
        "/drone/body/arm_3": Gf.Vec3f(0.3, 0.3, 0.3),
        "/drone/body/arm_4": Gf.Vec3f(0.3, 0.3, 0.3),
        
        # Motors - dark gray
        "/drone/body/motor_1": Gf.Vec3f(0.25, 0.25, 0.25),
        "/drone/body/motor_2": Gf.Vec3f(0.25, 0.25, 0.25),
        "/drone/body/motor_3": Gf.Vec3f(0.25, 0.25, 0.25),
        "/drone/body/motor_4": Gf.Vec3f(0.25, 0.25, 0.25),
        
        # Propellers - alternating user defined colors
        "/drone/prop_1": prop1_color,  # User defined
        "/drone/prop_2": prop2_color,  # User defined
        "/drone/prop_3": prop1_color,  # User defined
        "/drone/prop_4": prop2_color   # User defined
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
    
    # Add a light to ensure visibility
    light = UsdLux.DistantLight.Define(stage, "/Light")
    light.CreateIntensityAttr(500.0)
    light.CreateAngleAttr(0.53)
    light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    # Save the animated USD file
    stage.Export(usda_file)
    print(f"✅ Animated USD saved to {usda_file}")
    
    # Convert to USDZ
    try:
        UsdUtils.CreateNewUsdzPackage(
            Sdf.AssetPath(usda_file),
            output_file
        )
        print(f"✅ USDZ package created at {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating USDZ package: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create animated drone USDZ file')
    parser.add_argument('output_file', nargs='?', help='Path to the output USDZ file (optional)')
    parser.add_argument('--duration', type=float, default=3, help='Animation duration in seconds (default: 3)')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second (default: 24)')
    parser.add_argument('--body-color', type=str, default='0.1,0.1,0.1', help='RGB color for drone body (default: 0.1,0.1,0.1)')
    parser.add_argument('--prop1-color', type=str, default='0.8,0.0,0.0', help='RGB color for propellers 1 and 3 (default: 0.8,0.0,0.0)')
    parser.add_argument('--prop2-color', type=str, default='0.0,0.0,0.8', help='RGB color for propellers 2 and 4 (default: 0.0,0.0,0.8)')
    
    args = parser.parse_args()
    
    # Parse colors
    body_color = parse_color(args.body_color) or Gf.Vec3f(0.1, 0.1, 0.1)
    prop1_color = parse_color(args.prop1_color) or Gf.Vec3f(0.8, 0.0, 0.0)
    prop2_color = parse_color(args.prop2_color) or Gf.Vec3f(0.0, 0.0, 0.8)
    
    create_animated_drone(args.output_file, args.duration, args.fps, 
                         body_color, prop1_color, prop2_color)

if __name__ == "__main__":
    main()