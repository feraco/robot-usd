# Animated USDZ Files for RealityKit

## Overview

This project provides tools and examples for creating and using animated USDZ files in Xcode projects with RealityKit. The USDZ format is Apple's preferred 3D file format for AR experiences, and RealityKit is Apple's framework for working with AR content.

## What's Included

1. **Animated USDZ Files**:
   - `b2_animated.usdz` - Animated Unitree B2 robot
   - `g1_animated.usdz` - Animated Unitree G1 robot

2. **Conversion Tools**:
   - `create_animated_usdz.py` - Python script to convert USD files to animated USDZ
   - Animation scripts for specific robots (`animate_b2.py`, `animate_g1.py`)

3. **Documentation**:
   - `README.md` - Instructions for using USDZ files in Xcode with RealityKit
   - `XcodeProjectSetup.md` - Guide for setting up an Xcode project

4. **Example Code**:
   - `RobotARView.swift` - SwiftUI view for displaying USDZ models in AR

5. **Package**:
   - `robot_usdz_files.zip` - All files packaged together for easy distribution

## How It Works

1. **USD to USDZ Conversion**:
   - The Python scripts use the USD library to add animations to static USD models
   - Animations include joint rotations and body movements
   - The animated USD files are then converted to USDZ format

2. **Animation Techniques**:
   - Joint rotations for leg movements
   - Translation animations for body movement
   - Time-based animations with proper frame rates

3. **RealityKit Integration**:
   - The SwiftUI example shows how to load and display USDZ models
   - Includes code for playing animations automatically
   - Demonstrates AR placement on detected surfaces

## Usage

1. **Converting USD to USDZ**:
   ```bash
   python create_animated_usdz.py input.usd [output.usdz] [--duration 3] [--fps 24]
   ```

2. **Using in Xcode**:
   - Add USDZ files to your Xcode project
   - Use the provided SwiftUI code to display models in AR
   - See `XcodeProjectSetup.md` for detailed instructions

## Technical Details

- The USDZ files contain embedded animations at 24 frames per second
- Animations are set to loop automatically
- Models are optimized for mobile AR performance
- Compatible with iOS 14+ and Xcode 12+

## Future Improvements

- Add texture support for more realistic models
- Implement more complex animations (e.g., walking patterns)
- Add physics simulation for interactive models
- Support for model customization (colors, parts, etc.)
- Create a web-based converter for easier access