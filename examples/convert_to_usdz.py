#!/usr/bin/env python3

from pxr import Usd, UsdUtils
import os
import argparse

def convert_to_usdz(input_path, output_path=None):
    """
    Convert a USD file to USDZ format for use with RealityKit in Xcode.
    
    Args:
        input_path (str): Path to the input USD file
        output_path (str, optional): Path for the output USDZ file. If not provided,
                                    will use the same name as input with .usdz extension.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return False
    
    if output_path is None:
        # Use the same name but with .usdz extension
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.usdz"
    
    # Create the USDZ package
    result = UsdUtils.CreateNewARKitUsdzPackage(input_path, output_path)
    
    if result:
        print(f"Successfully created USDZ file: {output_path}")
        return True
    else:
        print(f"Failed to create USDZ file from {input_path}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert USD files to USDZ format for RealityKit")
    parser.add_argument("input_path", help="Path to the input USD file")
    parser.add_argument("--output", "-o", help="Path for the output USDZ file (optional)")
    
    args = parser.parse_args()
    convert_to_usdz(args.input_path, args.output)