# Animated Robot USDZ Files for RealityKit

## Overview

This project demonstrates how to create animated USD files and convert them to USDZ format for use in Xcode projects with RealityKit. The repository includes:

1. Python scripts to create animated 3D robot models
2. Tools to convert USD files to USDZ format
3. Example Swift code for integrating USDZ files in an iOS/iPadOS AR application
4. Documentation on how to structure an Xcode project

## Files Created

### USD/USDZ Files
- `examples/animated_robot.usda` - Simple animated robot in USD format
- `examples/animated_robot.usdz` - Simple robot converted to USDZ format
- `examples/complex_robot.usda` - Complex animated robot with multiple moving parts
- `examples/complex_robot.usdz` - Complex robot converted to USDZ format

### Python Scripts
- `examples/create_animated_robot.py` - Creates a simple animated robot
- `examples/create_complex_robot.py` - Creates a complex animated robot with multiple animations
- `examples/convert_to_usdz.py` - Converts USD files to USDZ format

### Swift/Xcode Integration
- `examples/RobotARView.swift` - SwiftUI view for displaying USDZ models in AR
- `examples/XcodeProjectStructure.md` - Guide for setting up an Xcode project

### Documentation
- `README.md` - Main documentation with usage instructions
- `SUMMARY.md` - This summary document

### Package
- `robot_usdz_files.zip` - Zip archive containing all necessary files for Xcode integration

## How to Use

1. Download the `robot_usdz_files.zip` file
2. Extract the contents
3. Follow the instructions in `XcodeProjectStructure.md` to set up your Xcode project
4. Add the USDZ files to your Xcode project
5. Implement the AR view using the provided `RobotARView.swift` as a reference

## Creating Your Own Animated USDZ Files

To create your own animated USDZ files:

1. Modify the Python scripts to create your own 3D models and animations
2. Run the scripts to generate USD files:
   ```
   python3 create_your_model.py
   ```
3. Convert the USD files to USDZ format:
   ```
   python3 convert_to_usdz.py your_model.usda
   ```
4. Add the resulting USDZ files to your Xcode project

## Requirements

- USD Core library (`pip install usd-core`)
- Python 3.6+
- Xcode 11+ for RealityKit development
- iOS/iPadOS 13+ for running AR applications