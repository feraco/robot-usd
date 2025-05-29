#!/usr/bin/env python3

from pxr import Usd, UsdGeom, UsdSkel, Sdf, Gf, Vt

def create_animated_robot(output_path):
    # Create a new stage
    stage = Usd.Stage.CreateNew(output_path)
    
    # Set up axis
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # Create a root xform
    root = UsdGeom.Xform.Define(stage, '/Robot')
    
    # Create a simple robot body (cube)
    body = UsdGeom.Cube.Define(stage, '/Robot/Body')
    body.AddScaleOp().Set(Gf.Vec3f(1.0, 1.5, 0.5))
    body.AddTranslateOp().Set(Gf.Vec3f(0, 1.5, 0))
    
    # Create robot head (sphere)
    head = UsdGeom.Sphere.Define(stage, '/Robot/Head')
    head.AddScaleOp().Set(Gf.Vec3f(0.5, 0.5, 0.5))
    head.AddTranslateOp().Set(Gf.Vec3f(0, 3.0, 0))
    
    # Create left arm
    left_arm = UsdGeom.Cylinder.Define(stage, '/Robot/LeftArm')
    left_arm.AddScaleOp().Set(Gf.Vec3f(0.2, 1.0, 0.2))
    left_arm.AddTranslateOp().Set(Gf.Vec3f(-1.2, 1.5, 0))
    left_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, -20))
    
    # Create right arm
    right_arm = UsdGeom.Cylinder.Define(stage, '/Robot/RightArm')
    right_arm.AddScaleOp().Set(Gf.Vec3f(0.2, 1.0, 0.2))
    right_arm.AddTranslateOp().Set(Gf.Vec3f(1.2, 1.5, 0))
    right_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 20))
    
    # Create left leg
    left_leg = UsdGeom.Cylinder.Define(stage, '/Robot/LeftLeg')
    left_leg.AddScaleOp().Set(Gf.Vec3f(0.25, 1.0, 0.25))
    left_leg.AddTranslateOp().Set(Gf.Vec3f(-0.5, 0, 0))
    
    # Create right leg
    right_leg = UsdGeom.Cylinder.Define(stage, '/Robot/RightLeg')
    right_leg.AddScaleOp().Set(Gf.Vec3f(0.25, 1.0, 0.25))
    right_leg.AddTranslateOp().Set(Gf.Vec3f(0.5, 0, 0))
    
    # Set default prim
    stage.SetDefaultPrim(root.GetPrim())
    
    # Add animation to the robot
    # Animate the robot's arms
    left_arm_rotate = left_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    right_arm_rotate = right_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    
    # Set animation time range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(48)
    
    # Create animation for left arm
    for frame in range(1, 49):
        time = Usd.TimeCode(frame)
        angle = -20 - 30 * abs(math.sin(frame * math.pi / 24))
        left_arm_rotate.Set(Gf.Vec3f(0, 0, angle), time)
    
    # Create animation for right arm
    for frame in range(1, 49):
        time = Usd.TimeCode(frame)
        angle = 20 + 30 * abs(math.sin(frame * math.pi / 24))
        right_arm_rotate.Set(Gf.Vec3f(0, 0, angle), time)
    
    # Add a simple bounce animation to the whole robot
    root_translate = root.AddTranslateOp()
    for frame in range(1, 49):
        time = Usd.TimeCode(frame)
        height = 0.2 * abs(math.sin(frame * math.pi / 12))
        root_translate.Set(Gf.Vec3f(0, height, 0), time)
    
    # Save the stage
    stage.Save()
    print(f"Created animated robot USD file at {output_path}")

if __name__ == "__main__":
    import math
    import os
    
    # Create the animated robot USD file
    create_animated_robot("/workspace/robot-usd/examples/animated_robot.usda")