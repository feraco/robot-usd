#!/usr/bin/env python3
from pxr import Usd, UsdGeom, UsdUtils, Sdf, Gf, UsdShade, UsdLux, Vt
import math
import os

def create_original_animated_crazyflie():
    # Input and output files
    input_file = "cf2x.usd"
    output_file = "cf2x_original_animated.usda"
    usdz_file = "cf2x_original_animated.usdz"
    
    print(f"Creating animated USDZ from original USD file: {input_file}")
    
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
                            
                            print(f"Copied nested mesh: {xform_child_path}")
                else:
                    print(f"Skipping unsupported prim type: {child_path}")
    
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
            
            # Get the original transform
            source_prop_xform = UsdGeom.Xformable(source_prop)
            
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
                            
                            print(f"Copied nested propeller mesh: {xform_child_path}")
            
            # Add rotation animation to propeller
            # Alternate direction: odd-numbered props CCW, even-numbered CW
            direction = -1 if i % 2 == 0 else 1
            rotate_op = prop_xform.AddRotateYOp(UsdGeom.XformOp.PrecisionDouble, "rotateY")
            
            # Create a continuous rotation animation
            for frame in range(1, 73):
                time = frame
                angle = direction * (720 / 24) * frame  # 720 degrees per second (2 rotations)
                rotate_op.Set(angle, time)
    
    # Add a subtle hovering motion to the entire drone
    hover_op = root.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble, "translate")
    
    # Create a subtle up/down hovering motion
    for frame in range(1, 73):
        time = frame
        height = 0.05 * math.sin(2 * math.pi * frame / 48)  # Up/down motion
        hover_op.Set(Gf.Vec3d(0, height, 0), time)
    
    # Copy materials
    source_looks = source_stage.GetPrimAtPath("/crazyflie/Looks")
    if source_looks:
        # Create Looks in the new stage
        looks = UsdGeom.Xform.Define(stage, "/crazyflie/Looks")
        
        # Copy all materials
        for material_prim in source_looks.GetChildren():
            material_path = str(material_prim.GetPath())
            
            # Create material
            material = UsdShade.Material.Define(stage, material_path)
            
            # Copy shader if it exists
            shader_path = f"{material_path}/Shader"
            source_shader = source_stage.GetPrimAtPath(shader_path)
            if source_shader:
                shader = UsdShade.Shader.Define(stage, shader_path)
                
                # Copy shader attributes
                source_shader_prim = UsdShade.Shader(source_shader)
                if source_shader_prim.GetIdAttr().Get():
                    shader.CreateIdAttr(source_shader_prim.GetIdAttr().Get())
                
                # Copy inputs
                for input_name in ["diffuseColor", "metallic", "roughness", "opacity"]:
                    source_input = source_shader_prim.GetInput(input_name)
                    if source_input and source_input.Get():
                        shader.CreateInput(input_name, source_input.GetTypeName()).Set(source_input.Get())
                
                print(f"Copied shader: {shader_path}")
            
            print(f"Copied material: {material_path}")
    
    # Add a light to ensure visibility
    light = UsdLux.DistantLight.Define(stage, "/Light")
    light.CreateIntensityAttr(500.0)
    light.CreateAngleAttr(0.53)
    light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    # Save the animated USD file
    stage.Export(output_file)
    print(f"✅ Original animated USD saved to {output_file}")
    
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
    create_original_animated_crazyflie()