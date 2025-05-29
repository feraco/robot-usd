#!/bin/bash

# Create a zip file with all the necessary files for Xcode/RealityKit
mkdir -p /workspace/robot-usd/dist

# Copy the USDZ files
cp /workspace/robot-usd/examples/*.usdz /workspace/robot-usd/dist/

# Copy the Swift example
cp /workspace/robot-usd/examples/RobotARView.swift /workspace/robot-usd/dist/

# Copy the Xcode project structure guide
cp /workspace/robot-usd/examples/XcodeProjectStructure.md /workspace/robot-usd/dist/

# Copy the README
cp /workspace/robot-usd/README.md /workspace/robot-usd/dist/

# Create the zip file
cd /workspace/robot-usd
zip -r robot_usdz_files.zip dist/

echo "Package created at /workspace/robot-usd/robot_usdz_files.zip"