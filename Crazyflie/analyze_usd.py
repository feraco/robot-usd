#!/usr/bin/env python3
from pxr import Usd, UsdGeom

def print_hierarchy(prim, indent=0):
    print(' ' * indent + f'- {prim.GetPath()}')
    for child in prim.GetChildren():
        print_hierarchy(child, indent + 2)

# Open the USD file
stage = Usd.Stage.Open('cf2x.usd')

print('Root prims:')
for prim in stage.GetPseudoRoot().GetChildren():
    print(f'- {prim.GetPath()}')

print('\nHierarchy:')
for prim in stage.GetPseudoRoot().GetChildren():
    print_hierarchy(prim)