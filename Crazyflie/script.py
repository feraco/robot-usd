from pxr import UsdUtils, Sdf

UsdUtils.CreateNewUsdzPackage(
    Sdf.AssetPath("cf2x_animated.usda"),  # wrap in Sdf.AssetPath
    "cf2x_animated.usdz"                  # output file
)

