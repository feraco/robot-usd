#!/usr/bin/env python3

from pxr import Usd, UsdGeom, Sdf, Gf, Vt
import math
import os

def create_complex_robot(output_path):
    # Create a new stage
    stage = Usd.Stage.CreateNew(output_path)
    
    # Set up axis
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # Create a root xform
    root = UsdGeom.Xform.Define(stage, '/ComplexRobot')
    
    # Create a simple robot body (cube)
    body = UsdGeom.Cube.Define(stage, '/ComplexRobot/Body')
    body.AddScaleOp().Set(Gf.Vec3f(1.0, 1.5, 0.5))
    body.AddTranslateOp().Set(Gf.Vec3f(0, 1.5, 0))
    
    # Create robot head (sphere)
    head = UsdGeom.Sphere.Define(stage, '/ComplexRobot/Head')
    head.AddScaleOp().Set(Gf.Vec3f(0.5, 0.5, 0.5))
    head.AddTranslateOp().Set(Gf.Vec3f(0, 3.0, 0))
    
    # Create eyes
    left_eye = UsdGeom.Sphere.Define(stage, '/ComplexRobot/Head/LeftEye')
    left_eye.AddScaleOp().Set(Gf.Vec3f(0.1, 0.1, 0.1))
    left_eye.AddTranslateOp().Set(Gf.Vec3f(-0.2, 0.1, 0.4))
    
    right_eye = UsdGeom.Sphere.Define(stage, '/ComplexRobot/Head/RightEye')
    right_eye.AddScaleOp().Set(Gf.Vec3f(0.1, 0.1, 0.1))
    right_eye.AddTranslateOp().Set(Gf.Vec3f(0.2, 0.1, 0.4))
    
    # Create upper arms
    left_upper_arm = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/LeftUpperArm')
    left_upper_arm.AddScaleOp().Set(Gf.Vec3f(0.2, 0.6, 0.2))
    left_upper_arm.AddTranslateOp().Set(Gf.Vec3f(-1.2, 2.0, 0))
    left_upper_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, -20))
    
    right_upper_arm = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/RightUpperArm')
    right_upper_arm.AddScaleOp().Set(Gf.Vec3f(0.2, 0.6, 0.2))
    right_upper_arm.AddTranslateOp().Set(Gf.Vec3f(1.2, 2.0, 0))
    right_upper_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 20))
    
    # Create lower arms
    left_lower_arm = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/LeftLowerArm')
    left_lower_arm.AddScaleOp().Set(Gf.Vec3f(0.15, 0.5, 0.15))
    left_lower_arm.AddTranslateOp().Set(Gf.Vec3f(-1.6, 1.2, 0))
    left_lower_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, -20))
    
    right_lower_arm = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/RightLowerArm')
    right_lower_arm.AddScaleOp().Set(Gf.Vec3f(0.15, 0.5, 0.15))
    right_lower_arm.AddTranslateOp().Set(Gf.Vec3f(1.6, 1.2, 0))
    right_lower_arm.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 20))
    
    # Create upper legs
    left_upper_leg = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/LeftUpperLeg')
    left_upper_leg.AddScaleOp().Set(Gf.Vec3f(0.25, 0.6, 0.25))
    left_upper_leg.AddTranslateOp().Set(Gf.Vec3f(-0.5, 0.6, 0))
    
    right_upper_leg = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/RightUpperLeg')
    right_upper_leg.AddScaleOp().Set(Gf.Vec3f(0.25, 0.6, 0.25))
    right_upper_leg.AddTranslateOp().Set(Gf.Vec3f(0.5, 0.6, 0))
    
    # Create lower legs
    left_lower_leg = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/LeftLowerLeg')
    left_lower_leg.AddScaleOp().Set(Gf.Vec3f(0.2, 0.5, 0.2))
    left_lower_leg.AddTranslateOp().Set(Gf.Vec3f(-0.5, 0, 0))
    
    right_lower_leg = UsdGeom.Cylinder.Define(stage, '/ComplexRobot/RightLowerLeg')
    right_lower_leg.AddScaleOp().Set(Gf.Vec3f(0.2, 0.5, 0.2))
    right_lower_leg.AddTranslateOp().Set(Gf.Vec3f(0.5, 0, 0))
    
    # Set default prim
    stage.SetDefaultPrim(root.GetPrim())
    
    # Set animation time range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(60)
    
    # Add animation to the robot parts
    # Get animation attributes
    left_upper_arm_rotate = left_upper_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    right_upper_arm_rotate = right_upper_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    left_lower_arm_rotate = left_lower_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    right_lower_arm_rotate = right_lower_arm.GetPrim().GetAttribute('xformOp:rotateXYZ')
    head_rotate = head.GetPrim().GetAttribute('xformOp:rotateXYZ')
    
    # Create head rotation animation
    head_rotate_op = head.AddRotateXYZOp()
    for frame in range(1, 61):
        time = Usd.TimeCode(frame)
        angle = 15 * math.sin(frame * math.pi / 15)
        head_rotate_op.Set(Gf.Vec3f(0, angle, 0), time)
    
    # Create animation for upper arms
    for frame in range(1, 61):
        time = Usd.TimeCode(frame)
        left_angle = -20 - 40 * abs(math.sin(frame * math.pi / 30))
        right_angle = 20 + 40 * abs(math.sin(frame * math.pi / 30))
        left_upper_arm_rotate.Set(Gf.Vec3f(0, 0, left_angle), time)
        right_upper_arm_rotate.Set(Gf.Vec3f(0, 0, right_angle), time)
    
    # Create animation for lower arms
    for frame in range(1, 61):
        time = Usd.TimeCode(frame)
        left_angle = -20 - 30 * abs(math.sin((frame + 5) * math.pi / 30))
        right_angle = 20 + 30 * abs(math.sin((frame + 5) * math.pi / 30))
        left_lower_arm_rotate.Set(Gf.Vec3f(0, 0, left_angle), time)
        right_lower_arm_rotate.Set(Gf.Vec3f(0, 0, right_angle), time)
    
    # Add a simple bounce animation to the whole robot
    root_translate = root.AddTranslateOp()
    for frame in range(1, 61):
        time = Usd.TimeCode(frame)
        height = 0.2 * abs(math.sin(frame * math.pi / 15))
        root_translate.Set(Gf.Vec3f(0, height, 0), time)
    
    # Add eye blinking animation
    left_eye_scale = left_eye.GetPrim().GetAttribute('xformOp:scale')
    right_eye_scale = right_eye.GetPrim().GetAttribute('xformOp:scale')
    
    for frame in range(1, 61):
        time = Usd.TimeCode(frame)
        # Blink every 20 frames
        if frame % 20 == 0:
            scale_y = 0.01  # Almost closed
        else:
            scale_y = 0.1  # Normal
        
        left_eye_scale.Set(Gf.Vec3f(0.1, scale_y, 0.1), time)
        right_eye_scale.Set(Gf.Vec3f(0.1, scale_y, 0.1), time)
    
    # Save the stage
    stage.Save()
    print(f"Created complex animated robot USD file at {output_path}")

if __name__ == "__main__":
    # Create the animated robot USD file
    create_complex_robot("/workspace/robot-usd/examples/complex_robot.usda")