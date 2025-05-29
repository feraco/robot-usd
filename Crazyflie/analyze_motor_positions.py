#!/usr/bin/env python3
from pxr import Usd, UsdGeom, Gf

# Open the USD file
stage = Usd.Stage.Open('cf2x.usd')

# Find the motor joints
motor_joints = [
    "/crazyflie/body/m1_joint",
    "/crazyflie/body/m2_joint",
    "/crazyflie/body/m3_joint",
    "/crazyflie/body/m4_joint"
]

print("Motor joint positions:")
for joint_path in motor_joints:
    joint = stage.GetPrimAtPath(joint_path)
    if joint:
        xformable = UsdGeom.Xformable(joint)
        # Get the local transform matrix
        local_transform = xformable.ComputeLocalToWorldTransform(0)
        # Extract the translation component
        translation = local_transform.ExtractTranslation()
        print(f"{joint_path}: {translation}")

# Find the propellers
propellers = [
    "/crazyflie/m1_prop",
    "/crazyflie/m2_prop",
    "/crazyflie/m3_prop",
    "/crazyflie/m4_prop"
]

print("\nPropeller positions:")
for prop_path in propellers:
    prop = stage.GetPrimAtPath(prop_path)
    if prop:
        xformable = UsdGeom.Xformable(prop)
        # Get the local transform matrix
        local_transform = xformable.ComputeLocalToWorldTransform(0)
        # Extract the translation component
        translation = local_transform.ExtractTranslation()
        print(f"{prop_path}: {translation}")

# Print the body visual components
body_visual_path = "/crazyflie/body/body_visual"
body_visual = stage.GetPrimAtPath(body_visual_path)
if body_visual:
    print("\nBody visual components:")
    for child in body_visual.GetChildren():
        print(f"- {child.GetPath()}")