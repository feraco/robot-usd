#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, UsdLux, Vt
import math
import os

def create_colored_crazyflie():
    # Input and output files
    input_file = "cf2x.usd"
    output_file = "cf2x_colored_animated.usda"
    usdz_file = "cf2x_colored_animated.usdz"
    
    print(f"Creating colored animated USDZ from original USD file: {input_file}")
    
    # Open the original USD file
    source_stage = Usd.Stage.Open(input_file)
    if not source_stage:
        print(f"❌ Error: Could not open {input_file}")
        return False
    
    # Create a new stage
    stage = Usd.Stage.CreateNew(output_file)
    
    # Set timeCodesPerSecond for proper playback
    stage.SetTimeCodesPerSecond(24)
    
    # Set frame range - 3 seconds at 24 fps
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(72)
    
    # Copy the root prim
    source_root = source_stage.GetPrimAtPath("/crazyflie")
    if not source_root:
        print("❌ Error: Could not find /crazyflie prim in source file")
        return False
    
    # Create a root prim in the new stage
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
        
        # Set shader properties
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
    source_body = source_stage.GetPrimAtPath(body_path)
    if source_body:
        # Create body in the new stage
        body = UsdGeom.Xform.Define(stage, body_path)
        
        # Copy all body visual components
        body_visual_path = f"{body_path}/body_visual"
        source_body_visual = source_stage.GetPrimAtPath(body_visual_path)
        if source_body_visual:
            body_visual = UsdGeom.Xform.Define(stage, body_visual_path)
            
            # Copy all visual components
            for visual_child in source_body_visual.GetChildren():
                child_path = str(visual_child.GetPath())
                child_name = visual_child.GetName()
                
                # Copy the mesh or geometry
                if visual_child.IsA(UsdGeom.Mesh):
                    # Create a new mesh
                    mesh = UsdGeom.Mesh.Define(stage, child_path)
                    
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
                    
                    print(f"Copied mesh: {child_path}")
                elif visual_child.IsA(UsdGeom.Xform):
                    # Create a new xform
                    xform = UsdGeom.Xform.Define(stage, child_path)
                    
                    # Copy all children recursively
                    for xform_child in visual_child.GetChildren():
                        if xform_child.IsA(UsdGeom.Mesh):
                            xform_child_path = str(xform_child.GetPath())
                            xform_mesh = UsdGeom.Mesh.Define(stage, xform_child_path)
                            
                            # Copy mesh data
                            source_xform_mesh = UsdGeom.Mesh(xform_child)
                            if source_xform_mesh.GetPointsAttr().Get():
                                xform_mesh.CreatePointsAttr().Set(source_xform_mesh.GetPointsAttr().Get())
                            
                            if source_xform_mesh.GetFaceVertexCountsAttr().Get():
                                xform_mesh.CreateFaceVertexCountsAttr().Set(source_xform_mesh.GetFaceVertexCountsAttr().Get())
                            
                            if source_xform_mesh.GetFaceVertexIndicesAttr().Get():
                                xform_mesh.CreateFaceVertexIndicesAttr().Set(source_xform_mesh.GetFaceVertexIndicesAttr().Get())
                            
                            if source_xform_mesh.GetNormalsAttr().Get():
                                xform_mesh.CreateNormalsAttr().Set(source_xform_mesh.GetNormalsAttr().Get())
                            
                            # Copy UV coordinates if they exist
                            primvars = UsdGeom.PrimvarsAPI(source_xform_mesh)
                            st_primvar = primvars.GetPrimvar("st")
                            if st_primvar:
                                mesh_primvars = UsdGeom.PrimvarsAPI(xform_mesh)
                                mesh_primvars.CreatePrimvar("st", st_primvar.GetTypeName(), st_primvar.GetInterpolation()).Set(st_primvar.Get())
                            
                            # Apply material
                            UsdShade.MaterialBindingAPI(xform_mesh).Bind(materials["body"])
                            
                            print(f"Copied nested mesh: {xform_child_path}")
                else:
                    print(f"Skipping unsupported prim type: {child_path}")
    
    # Define propeller positions (from the analysis)
    propeller_positions = [
        Gf.Vec3d(0.031, -0.031, 0.021),  # m1_prop
        Gf.Vec3d(-0.031, -0.031, 0.021), # m2_prop
        Gf.Vec3d(-0.031, 0.031, 0.021),  # m3_prop
        Gf.Vec3d(0.031, 0.031, 0.021)    # m4_prop
    ]
    
    # Copy the propellers
    propeller_paths = [
        "/crazyflie/m1_prop",
        "/crazyflie/m2_prop",
        "/crazyflie/m3_prop",
        "/crazyflie/m4_prop"
    ]
    
    for i, prop_path in enumerate(propeller_paths):
        source_prop = source_stage.GetPrimAtPath(prop_path)
        if source_prop:
            # Create propeller in the new stage
            prop = UsdGeom.Xform.Define(stage, prop_path)
            prop_xform = UsdGeom.Xformable(prop.GetPrim())
            
            # Set the propeller position
            translate_op = prop_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
            translate_op.Set(propeller_positions[i])
            
            # Copy all propeller children (the actual mesh)
            for prop_child in source_prop.GetChildren():
                child_path = str(prop_child.GetPath())
                
                if prop_child.IsA(UsdGeom.Mesh):
                    # Create a new mesh
                    mesh = UsdGeom.Mesh.Define(stage, child_path)
                    
                    # Copy mesh data
                    source_mesh = UsdGeom.Mesh(prop_child)
                    if source_mesh.GetPointsAttr().Get():
                        mesh.CreatePointsAttr().Set(source_mesh.GetPointsAttr().Get())
                    
                    if source_mesh.GetFaceVertexCountsAttr().Get():
                        mesh.CreateFaceVertexCountsAttr().Set(source_mesh.GetFaceVertexCountsAttr().Get())
                    
                    if source_mesh.GetFaceVertexIndicesAttr().Get():
                        mesh.CreateFaceVertexIndicesAttr().Set(source_mesh.GetFaceVertexIndicesAttr().Get())
                    
                    if source_mesh.GetNormalsAttr().Get():
                        mesh.CreateNormalsAttr().Set(source_mesh.GetNormalsAttr().Get())
                    
                    # Copy UV coordinates if they exist
                    primvars = UsdGeom.PrimvarsAPI(source_mesh)
                    st_primvar = primvars.GetPrimvar("st")
                    if st_primvar:
                        mesh_primvars = UsdGeom.PrimvarsAPI(mesh)
                        mesh_primvars.CreatePrimvar("st", st_primvar.GetTypeName(), st_primvar.GetInterpolation()).Set(st_primvar.Get())
                    
                    # Apply material based on propeller type
                    if "ccw" in child_path:
                        UsdShade.MaterialBindingAPI(mesh).Bind(materials["propeller_ccw"])
                    else:
                        UsdShade.MaterialBindingAPI(mesh).Bind(materials["propeller_cw"])
                    
                    print(f"Copied propeller mesh: {child_path}")
                elif prop_child.IsA(UsdGeom.Xform):
                    # Create a new xform
                    xform = UsdGeom.Xform.Define(stage, child_path)
                    
                    # Copy all children recursively
                    for xform_child in prop_child.GetChildren():
                        if xform_child.IsA(UsdGeom.Mesh):
                            xform_child_path = str(xform_child.GetPath())
                            xform_mesh = UsdGeom.Mesh.Define(stage, xform_child_path)
                            
                            # Copy mesh data
                            source_xform_mesh = UsdGeom.Mesh(xform_child)
                            if source_xform_mesh.GetPointsAttr().Get():
                                xform_mesh.CreatePointsAttr().Set(source_xform_mesh.GetPointsAttr().Get())
                            
                            if source_xform_mesh.GetFaceVertexCountsAttr().Get():
                                xform_mesh.CreateFaceVertexCountsAttr().Set(source_xform_mesh.GetFaceVertexCountsAttr().Get())
                            
                            if source_xform_mesh.GetFaceVertexIndicesAttr().Get():
                                xform_mesh.CreateFaceVertexIndicesAttr().Set(source_xform_mesh.GetFaceVertexIndicesAttr().Get())
                            
                            if source_xform_mesh.GetNormalsAttr().Get():
                                xform_mesh.CreateNormalsAttr().Set(source_xform_mesh.GetNormalsAttr().Get())
                            
                            # Copy UV coordinates if they exist
                            primvars = UsdGeom.PrimvarsAPI(source_xform_mesh)
                            st_primvar = primvars.GetPrimvar("st")
                            if st_primvar:
                                mesh_primvars = UsdGeom.PrimvarsAPI(xform_mesh)
                                mesh_primvars.CreatePrimvar("st", st_primvar.GetTypeName(), st_primvar.GetInterpolation()).Set(st_primvar.Get())
                            
                            # Apply material based on propeller type
                            if "ccw" in xform_child_path:
                                UsdShade.MaterialBindingAPI(xform_mesh).Bind(materials["propeller_ccw"])
                            else:
                                UsdShade.MaterialBindingAPI(xform_mesh).Bind(materials["propeller_cw"])
                            
                            print(f"Copied nested propeller mesh: {xform_child_path}")
            
            # Add rotation animation to propeller
            # Alternate direction: odd-numbered props CCW, even-numbered CW
            direction = -1 if i % 2 == 0 else 1
            rotate_op = prop_xform.AddRotateZOp(UsdGeom.XformOp.PrecisionDouble, "rotateZ")
            
            # Create a continuous rotation animation
            for frame in range(1, 73):
                time = frame
                angle = direction * (720 / 24) * frame  # 720 degrees per second (2 rotations)
                rotate_op.Set(angle, time)
    
    # Add a light to ensure visibility
    light = UsdLux.DistantLight.Define(stage, "/Light")
    light.CreateIntensityAttr(500.0)
    light.CreateAngleAttr(0.53)
    light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    # Save the animated USD file
    stage.Export(output_file)
    print(f"✅ Colored animated USD saved to {output_file}")
    
    # Convert to USDZ
    try:
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
    create_colored_crazyflie()