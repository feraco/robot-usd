#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, UsdLux, Vt
import math
import os
import subprocess

def create_ios_compatible_crazyflie():
    # Input and output files
    input_file = "cf2x.usd"
    output_file = "cf2x_ios_animated.usda"
    usdz_file = "cf2x_ios_animated.usdz"
    
    print(f"Creating iOS-compatible animated USDZ from original USD file: {input_file}")
    
    # Open the original USD file
    source_stage = Usd.Stage.Open(input_file)
    if not source_stage:
        print(f"❌ Error: Could not open {input_file}")
        return False
    
    # Create a new stage
    stage = Usd.Stage.CreateNew(output_file)
    
    # Set up for animation - iOS/macOS typically uses 30fps
    stage.SetStartTimeCode(0)
    stage.SetEndTimeCode(60)
    stage.SetTimeCodesPerSecond(30)
    
    # Create a root prim
    root = UsdGeom.Xform.Define(stage, "/crazyflie")
    stage.SetDefaultPrim(root.GetPrim())
    
    # Define colors for different parts
    colors = {
        "body": Gf.Vec3f(0.2, 0.2, 0.2),        # Dark gray for main body
        "battery": Gf.Vec3f(0.1, 0.1, 0.7),     # Blue for battery
        "battery_holder": Gf.Vec3f(0.7, 0.1, 0.1), # Red for battery holder
        "pin_headers": Gf.Vec3f(0.8, 0.8, 0.8),  # Light gray for pin headers
        "motor_mount": Gf.Vec3f(0.1, 0.7, 0.1),  # Green for motor mounts
        "propeller_ccw": Gf.Vec3f(1.0, 0.5, 0.0), # Orange for CCW propellers
        "propeller_cw": Gf.Vec3f(0.0, 0.5, 1.0)   # Light blue for CW propellers
    }
    
    # Create materials for each color
    materials = {}
    for part_name, color in colors.items():
        material_path = f"/crazyflie/Materials/{part_name}_material"
        material = UsdShade.Material.Define(stage, material_path)
        shader = UsdShade.Shader.Define(stage, f"{material_path}/Shader")
        
        # Set shader properties for iOS compatibility
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0)
        
        # Connect shader to material
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        # Store material for later use
        materials[part_name] = material
    
    # Copy the body and its children
    body_path = "/crazyflie/body"
    source_body = source_stage.GetPrimAtPath("/crazyflie/body")
    if source_body:
        # Create body in the new stage
        body = UsdGeom.Xform.Define(stage, body_path)
        
        # Copy all body visual components
        body_visual_path = f"{body_path}/body_visual"
        source_body_visual = source_stage.GetPrimAtPath(f"/crazyflie/body/body_visual")
        if source_body_visual:
            body_visual = UsdGeom.Xform.Define(stage, body_visual_path)
            
            # Copy all visual components
            for visual_child in source_body_visual.GetChildren():
                child_path = str(visual_child.GetPath())
                new_child_path = child_path.replace("/crazyflie/body/body_visual", body_visual_path)
                child_name = visual_child.GetName()
                
                # Copy the mesh or geometry
                if visual_child.IsA(UsdGeom.Mesh):
                    # Create a new mesh
                    mesh = UsdGeom.Mesh.Define(stage, new_child_path)
                    
                    # Copy points
                    source_mesh = UsdGeom.Mesh(visual_child)
                    if source_mesh.GetPointsAttr().Get():
                        mesh.CreatePointsAttr().Set(source_mesh.GetPointsAttr().Get())
                    
                    # Copy face vertex counts
                    if source_mesh.GetFaceVertexCountsAttr().Get():
                        mesh.CreateFaceVertexCountsAttr().Set(source_mesh.GetFaceVertexCountsAttr().Get())
                    
                    # Copy face vertex indices
                    if source_mesh.GetFaceVertexIndicesAttr().Get():
                        mesh.CreateFaceVertexIndicesAttr().Set(source_mesh.GetFaceVertexIndicesAttr().Get())
                    
                    # Copy normals if they exist
                    if source_mesh.GetNormalsAttr().Get():
                        mesh.CreateNormalsAttr().Set(source_mesh.GetNormalsAttr().Get())
                    
                    # Copy UV coordinates if they exist
                    primvars = UsdGeom.PrimvarsAPI(source_mesh)
                    st_primvar = primvars.GetPrimvar("st")
                    if st_primvar:
                        mesh_primvars = UsdGeom.PrimvarsAPI(mesh)
                        mesh_primvars.CreatePrimvar("st", st_primvar.GetTypeName(), st_primvar.GetInterpolation()).Set(st_primvar.Get())
                    
                    # Apply material based on part name
                    if child_name in materials:
                        UsdShade.MaterialBindingAPI(mesh).Bind(materials[child_name])
                    elif child_name == "cf_body_001" or child_name == "Cylinder":
                        UsdShade.MaterialBindingAPI(mesh).Bind(materials["body"])
                    
                    print(f"Copied mesh: {new_child_path}")
    
    # Define propeller positions (from the analysis)
    propeller_positions = [
        Gf.Vec3d(0.031, -0.031, 0.021),  # m1_prop
        Gf.Vec3d(-0.031, -0.031, 0.021), # m2_prop
        Gf.Vec3d(-0.031, 0.031, 0.021),  # m3_prop
        Gf.Vec3d(0.031, 0.031, 0.021)    # m4_prop
    ]
    
    # Create propellers with animation
    propeller_names = ["m1_prop", "m2_prop", "m3_prop", "m4_prop"]
    propeller_types = ["ccw", "cw", "ccw", "cw"]  # Alternating CCW and CW
    
    for i, (prop_name, prop_type, position) in enumerate(zip(propeller_names, propeller_types, propeller_positions)):
        # Create propeller group
        prop_path = f"/crazyflie/{prop_name}"
        prop = UsdGeom.Xform.Define(stage, prop_path)
        
        # Set position
        prop_xform = UsdGeom.Xformable(prop)
        translate_op = prop_xform.AddTranslateOp()
        translate_op.Set(position)
        
        # Find source propeller mesh
        source_prop_mesh = None
        source_prop = source_stage.GetPrimAtPath(f"/crazyflie/{prop_name}")
        if source_prop:
            for child in source_prop.GetChildren():
                if child.IsA(UsdGeom.Mesh):
                    source_prop_mesh = UsdGeom.Mesh(child)
                    break
        
        if source_prop_mesh:
            # Create propeller mesh
            mesh_path = f"{prop_path}/{prop_type}_prop"
            mesh = UsdGeom.Mesh.Define(stage, mesh_path)
            
            # Copy mesh data
            if source_prop_mesh.GetPointsAttr().Get():
                mesh.CreatePointsAttr().Set(source_prop_mesh.GetPointsAttr().Get())
            
            if source_prop_mesh.GetFaceVertexCountsAttr().Get():
                mesh.CreateFaceVertexCountsAttr().Set(source_prop_mesh.GetFaceVertexCountsAttr().Get())
            
            if source_prop_mesh.GetFaceVertexIndicesAttr().Get():
                mesh.CreateFaceVertexIndicesAttr().Set(source_prop_mesh.GetFaceVertexIndicesAttr().Get())
            
            if source_prop_mesh.GetNormalsAttr().Get():
                mesh.CreateNormalsAttr().Set(source_prop_mesh.GetNormalsAttr().Get())
            
            # Copy UV coordinates if they exist
            primvars = UsdGeom.PrimvarsAPI(source_prop_mesh)
            st_primvar = primvars.GetPrimvar("st")
            if st_primvar:
                mesh_primvars = UsdGeom.PrimvarsAPI(mesh)
                mesh_primvars.CreatePrimvar("st", st_primvar.GetTypeName(), st_primvar.GetInterpolation()).Set(st_primvar.Get())
            
            # Apply material based on propeller type
            material_key = f"propeller_{prop_type}"
            UsdShade.MaterialBindingAPI(mesh).Bind(materials[material_key])
            
            print(f"Created propeller mesh: {mesh_path}")
            
            # Add rotation animation directly to the propeller mesh
            # For iOS compatibility, we'll use a different approach
            # We'll create a separate rotation attribute and animate that
            mesh_xform = UsdGeom.Xformable(mesh.GetPrim())
            
            # Create a rotation attribute
            rotation_attr = mesh.GetPrim().CreateAttribute("xformOp:rotateZ", Sdf.ValueTypeNames.Double)
            rotation_attr.SetCustom(True)
            
            # Set the rotation order
            order_attr = mesh.GetPrim().CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray)
            order_attr.Set(["xformOp:translate", "xformOp:rotateZ"])
            
            # Create animation
            direction = -1 if prop_type == "ccw" else 1
            for frame in range(0, 61):
                time = frame
                angle = direction * 6.0 * frame  # 6 degrees per frame (180 degrees per second at 30fps)
                rotation_attr.Set(angle, time)
        else:
            print(f"⚠️ Warning: Could not find source propeller mesh for {prop_name}")
    
    # Add a light to ensure visibility
    light = UsdLux.DistantLight.Define(stage, "/Light")
    light.CreateIntensityAttr(500.0)
    light.CreateAngleAttr(0.53)
    light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    # Save the animated USD file
    stage.Export(output_file)
    print(f"✅ iOS-compatible animated USD saved to {output_file}")
    
    # Convert to USDZ using the command-line tool for better iOS compatibility
    try:
        # First try using the Python API
        UsdUtils.CreateNewUsdzPackage(
            Sdf.AssetPath(output_file),
            usdz_file
        )
        print(f"✅ USDZ package created at {usdz_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating USDZ package: {e}")
        return False

if __name__ == "__main__":
    create_ios_compatible_crazyflie()