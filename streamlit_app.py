import streamlit as st
from numpy import array
from pybimstab.slope import NaturalSlope
from pybimstab.watertable import WaterTable
from pybimstab.bim import BlocksInMatrix
from pybimstab.slipsurface import CircularSurface
from pybimstab.slipsurface import TortuousSurface
from pybimstab.slices import MaterialParameters, Slices
from pybimstab.slopestabl import SlopeStabl
import numpy as np

st.set_page_config(layout="wide")


with st.sidebar:
    depth = st.number_input("Depth of Excavation", min_value=15, max_value=60, value=30, step=1)
    layer1_thck = st.number_input("Soil Layer Thickness", min_value=5, max_value=60, value=5, step=1)
    layer1_thck = st.number_input("Soft Rock Layer Thickness", min_value=5, max_value=60, value=5, step=1)
    calculate = st.button("Calculate")

st.title("Slope Stability Analysis - without soil nail")
st.subheader("Basic Design Parameters")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Slope of each soil type")
    st.write("1. Slope in Soil (H:V) = 1.5:1")
    st.write("2. Slope in Rock (H:V) = 2:1")
    st.write("3. Slope in Hard Rock (H:V) = 4:1 ")

    st.subheader("Soil Strength Parameters")
    st.write("1. Cohesive Strength = 60 kPa")
    st.write("2. Friction Angle    = 30")

with col2:
    st.subheader("Bench Width and Height")
    st.write("1. Bench in Soil at every 5 meters")
    st.write("2. Bench in Rock at every  5 meters")
    st.write("3. Bench in Hard Rock at every 5 meters")
    st.write(" Bench width will be 2.5 m., and every 15 m will be 10 m. bench")

# """Define Soil Layer"""
depth = 57  # Height from Top of Rail

soil_layer1 = 17
soil_layer2 = 31

# """Define Slope"""
slope1 = 1.5  # H:1
slope2 = 1  # H:1
slope3 = 0.25

# """Typical Bench Width"""
bench_height1 = 5
bench_height2 = 5
bench_height3 = 4.5

# """Geometry"""

x = [0]
y = [0]
distance = 0
# Case 1: 2 Layers: layer1 + layer2 > depth
if depth < (soil_layer1 + soil_layer2):
    for bench in range(round(depth / bench_height3)):
        height = bench_height2 * (bench + 1)
        if height <= (depth - soil_layer1):
            x.append(bench_height2 * slope2)
        else:
            x.append(bench_height1 * slope1)
else:  # Case 2: depth > (soil_layer1 + soil_layer2): excavation below soil_layer2
    for bench in range(round(depth / bench_height3)):
        height = bench_height3 * (bench + 1)
        if height <= (depth - soil_layer1 - soil_layer2):
            x.append(bench_height3 * slope3)
        elif height <= (depth - soil_layer1):
            x.append(bench_height2 * slope2)
        else:
            x.append(bench_height1 * slope1)

for bench in range(round(depth / bench_height3)):
    height = (bench_height3 * (bench + 1))
    if height > depth:
        y.append(depth)
    elif height < (depth - soil_layer1 - soil_layer2):
        y.append(bench_height3 * (bench + 1))
    elif height > (depth - soil_layer1 - soil_layer2) and (height < depth - soil_layer1):
        y.append(bench_height2 * (bench + 1))
    else:
        y.append(bench_height3 * (bench + 1))

y.reverse()
x.reverse()

x = x[:-1]
x.insert(0, 0)
for i in range(len(x) - 1):
    x[i + 1] = x[i] + x[i + 1]

print(f'Horizontal: {x}')
# for i in range(len(y)):
#  y[i]=y[i]+depth
y.append(0)
x.append(x[-1] + depth)
x.insert(0, -depth)
y.insert(0, y[0])
print(f'Vertical: {y}')
terrainCoordinates = array([x, y])
slope = NaturalSlope(terrainCoordinates)
bim = BlocksInMatrix(slopeCoords=slope.coords, blockProp=0.01, tileSize=0.5, seed=123)
print(slope.maxDepth())


# Add bench
def add_bench(x, y, height, bench_width):
    pos = y.index(height)
    y.insert(pos, y[pos])
    x.insert(pos, x[pos])
    posx = pos + 1
    for index in range(len(x[pos:]) - 1):
        x[posx + index] = x[posx + index] + bench_width
    return x, y


num_of_bench = len(y)
bench_level = y[2:(num_of_bench - 2)]
print(bench_level)
x1 = x
y1 = y
for lev in bench_level:
    x1, y1 = add_bench(x1, y1, lev, 1.5)

print(max(x1))
print(f'Horizontal:{x1}')
print(f'Vertical:v{y1}')
terrainCoordinates = array([x1, y1])
slope = NaturalSlope(terrainCoordinates)
bim = BlocksInMatrix(slopeCoords=slope.coords, blockProp=0.05, tileSize=0.5, seed=123)

# """Increasing Benching Width to 10 meters at every 15 m height"""
print(bench_level)
bench_level.reverse()
bench_at = bench_level[2::3]
print(bench_at)
for bench in bench_at:
    x1, y1 = add_bench(x1, y1, bench, 7.5)

print(max(x1))
print(f'Horizontal:{x1}')
print(f'Vertical:v{y1}')
terrainCoordinates = array([x1, y1])
slope = NaturalSlope(terrainCoordinates)
bim = BlocksInMatrix(slopeCoords=slope.coords, blockProp=0.05, tileSize=0.5, seed=123)
print(slope.maxDepth())

A = -x1[0]
B = x1[-1]
print(A, B)

watertabDepths = array([[0, round(max(x1)) / 3, round(max(x1)) * 2 / 3, max(x1)],
                        [2.5, 5, 5, 0]])
watertable = WaterTable(slopeCoords=slope.coords,
                        watertabDepths=watertabDepths,
                        smoothFactor=2)
print(watertable.defineStructre())
print(f'furthest node: {max(x1)}')
print(f'max depth: {slope.maxDepth()}')
preferredPath = CircularSurface(
    slopeCoords=slope.coords, dist1=A, dist2=B, radius=(B - A))
surface = TortuousSurface(
    bim, dist1=A, dist2=B, heuristic='euclidean',
    reverseLeft=False, reverseUp=False, smoothFactor=1,
    preferredPath=preferredPath.coords, prefPathFact=1)
material = MaterialParameters(
    cohesion=80, frictAngle=34, unitWeight=19,
    blocksUnitWeight=21, wtUnitWeight=9.8)
slices = Slices(
    material=material, slipSurfCoords=surface.coords,
    slopeCoords=slope.coords, numSlices=20,
    watertabCoords=watertable.coords, bim=bim)
stabAnalysis = SlopeStabl(slices, seedFS=2, Kh=0, maxLambda=1)
if calculate:
    fig = stabAnalysis.plot()
    fig.savefig('FS.png')
    st.pyplot(fig)
