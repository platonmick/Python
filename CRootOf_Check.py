from sympy import cyclotomic_poly, CRootOf
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, Circle
import numpy as np


def make_rectangles(intervals):
    return [ Rectangle((i.ax, i.ay), i.dx, i.dy) for i in intervals ]

def make_points(m):
    return {'x': np.cos( 2 * np.pi * np.arange(1, m) / m),
            'y': np.sin( 2 * np.pi * np.arange(1, m) / m)}

def draw(rectangles, points):
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(4.3, 4), layout='constrained')
    ax.set(xlim=(-1.1,1.1), ylim = (-1.1, 1.1))

    pc = PatchCollection(rectangles[:m - 2], facecolor='r', alpha=0.5,
                         edgecolor='none')
    rectangle_max = rectangles[m - 2]
    rectangle_max.set(facecolor='y', alpha=0.5)
    circle = plt.Circle((0,0), 1, color='b', fill = False)

    # Add patches to axes
    ax.add_patch(circle)
    ax.add_collection(pc)
    ax.add_patch(rectangle_max)
    ax.scatter('x', 'y', data=points)
    for i in range(len(rectangles)):
        r = rectangles[i]
        ax.annotate(i, r.get_corners()[2])

m = 13
T = cyclotomic_poly(m)
roots = [ CRootOf(T, i) for i in range(m - 1) ]
intervals = [ roots[i]._get_interval() for i in range(m - 1) ]
rectangles = make_rectangles(intervals)
points = make_points(m)

for i in range(m-1):
    print(f'{i}  {intervals[i]}')

draw(rectangles, points)
plt.show()
  