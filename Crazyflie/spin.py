from pxr import Usd, UsdGeom

input_file = "cf2x_clean.usda"
output_file = "cf2x_ready.usda"

stage = Usd.Stage.Open(input_file)
stage.SetDefaultPrim(stage.GetPrimAtPath("/crazyflie/body/body_visual"))  # adjust to actual animated root

# Optional: set timeCodesPerSecond for proper playback
stage.SetMetadata("timeCodesPerSecond", 24)

stage.Save()
print("✅ USD cleaned and ready.")
