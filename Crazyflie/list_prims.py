from pxr import Usd

stage = Usd.Stage.Open("cf2x.usd")

for prim in stage.Traverse():
    print(prim.GetPath())
