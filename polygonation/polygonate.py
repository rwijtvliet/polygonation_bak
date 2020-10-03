# -*- coding: utf-8 -*-
"""
Module to turn a set of points into a set of convex nonoverlapping polygons.
Done by identifying the removable walls, and then removing one of them.
Rinse-repeat until no further walls can be removed.

Not optimized or anything. For example, all candidiates are recalculated
after removing a wall, and the Delaunay grid is calculated several times.

2020-10
rwijtvliet@gmail.com
"""

import numpy as np
from matplotlib import pylab as plt
from scipy.spatial import Delaunay, ConvexHull
from typing import Iterable


# Find out, which lines could be removed and keep convexness of shape.
# Method: check each pair of neighboring shapes, and see, if union of them
# would still be convex.
# How to check for convexness of a shape:
# . possibility 1: all points are in the convex hull.
# . possibility 2: going around the polygon, the angle change between 
#   consequetive lines always has the same sign --> only works in 2D


def candidates(points, shapes=None, neighbors_of_shapes=None):
    """
    Find the walls that could be removed while still keeping the resulting 
    shape convex. Also store additional information, such as wall length
    and existing angles.
    """
    if shapes is None or neighbors_of_shapes is None:
        delaunay = Delaunay(points)
        shapes, neighbors_of_shapes = delaunay.simplices, delaunay.neighbors
    
    def prepshape(shape, wall): #rotate/flip shape so, that wall[0] is at start and wall[1] is at end.
        while len(np.intersect1d(shape[0:2], wall)) != 2:
            shape = np.roll(shape, 1)
        shape = np.roll(shape, -1) #one vwall vertice at start, the other at the end.
        if shape[0] == wall[1]:
            shape = np.flip(shape) #vwall[0] is at beginning, vwall[1] is at end
        return shape
    def vec(*vi):
        return points[vi[1]] - points[vi[0]]
    def cosangle(vecA, vecB):
        cosangle = np.dot(vecA, vecB) / (np.linalg.norm(vecA) * np.linalg.norm(vecB))
        return abs(cosangle)
    
    candidates = []
    for si1, neighbors in enumerate(neighbors_of_shapes):
        shape1 = shapes[si1]
        for si2 in neighbors:
            if si1 > si2: continue #only add each wall once
            shape2 = shapes[si2] 
            # Find vertices of shared wall.
            wall = np.intersect1d(shape1, shape2)
            # Prepare by putting wall vertice 0 at position 0 in each shape
            shape1, shape2 = prepshape(shape1, wall), prepshape(shape2, wall)
            # Get candidate-polygon
            shape3 = [*shape1[:-1], *np.flip(shape2)[:-1]]
            if len(ConvexHull(points[shape3]).vertices) == len(shape3):
                #Yes, it's still convex, so wall can be removed
                wallvec = vec(*wall)
                walllen = np.linalg.norm(wallvec)
                cosangles = np.array([cosangle(wallvec, vec(*vi)) for vi in
                             [shape1[:2], shape1[-2:], shape2[:2], shape2[-2:]]])
                candidates.append({
                    'wall': [*wall],
                    'si': [si1, si2], 
                    'shape3': shape3,
                    'charst': {'len':walllen, 'cosangles': -np.sort(-cosangles)}})
    return candidates

def polygonate(points:Iterable, pickwall:str):
    """
    Turn a set of points into a set of convex polygons.
    
    Arguments:
        points: Iterable of (x, y)-points
        pickwall: 
            'long'(est) to remove the longest walls first;
            'short'(est) to remove the shortest walls first; 
            'sharp'(est) to remove the most accute angles first (default)
    
    Returns:
        array of polygons; each polygon being a list of point-indices for its
            vertices.
    """
    delaunay = Delaunay(points)
    shapes = delaunay.simplices.tolist()
    neighbors_of_shapes = [[si for si in neighbors if si != -1] 
                           for neighbors in delaunay.neighbors]
    if pickwall.startswith('short'):
        pickwallfunc = lambda cands: np.argmin([cand['charst']['len'] for cand in cands])
    elif pickwall.startswith('long'):
        pickwallfunc = lambda cands: np.argmax([cand['charst']['len'] for cand in cands])
    else:
        pickwallfunc = lambda cands: np.argmax([cand['charst']['cosangles'][0] for cand in cands])
        
    def melt(si1, si2, shape3): #remove shapes with indices si1 and si2. Add shape with vertices shape3.
        nonlocal shapes, neighbors_of_shapes
        if si1 > si2: si1, si2 = si2, si1
        shapes.pop(si2)
        shapes.pop(si1)  
        si3 = len(shapes)
        shapes.append(shape3)
        nei3 = [*neighbors_of_shapes.pop(si2), *neighbors_of_shapes.pop(si1)]
        nei3 = [si for si in nei3 if si != si1 and si != si2]
        neighbors_of_shapes.append(nei3)
        neighbors_of_shapes2 = []
        for neighbors in neighbors_of_shapes:
            neighbors2 = []
            for si in neighbors:
                if si == si1 or si == si2:
                    neighbors2.append(si3)
                elif si < si1:
                    neighbors2.append(si)  
                elif si < si2:
                    neighbors2.append(si-1)
                else:
                    neighbors2.append(si-2)
            neighbors_of_shapes2.append(neighbors2)
        neighbors_of_shapes = neighbors_of_shapes2
    
    while True:
        cands = candidates(points, shapes, neighbors_of_shapes)
       
        if len(cands) == 0: break
        # Find which one to remove.
        picked = cands[pickwallfunc(cands)]
        melt(*picked['si'], picked['shape3'])

        # fig, ax = plt.subplots(1,1, figsize=(10,10))
        # plotpolygon(ax, points, shapes)
        # ax.plot(*points[picked['wall']].T, 'r')
    
    return shapes


# Draw and sample use.

def plotpoints(ax, points, **kwargs):
    ax.plot(*points.T, 'ko', **kwargs)
def plotdelaunay(ax, points, **kwargs):
    delaunay = Delaunay(points)
    indptr, indices = delaunay.vertex_neighbor_vertices
    for vi1 in np.arange(len(points)):
        for vi2 in indices[indptr[vi1]:indptr[vi1+1]]:
            if vi1 < vi2:
                ax.plot(*points[[vi1, vi2],:].T, 'k', **{'alpha':1, **kwargs})
def plotremovablewalls(ax, points, **kwargs):
    delaunay = Delaunay(points)
    cands = candidates(points, delaunay.simplices, delaunay.neighbors)
    for w in [cand['wall'] for cand in cands]:
        ax.plot(*points[w, :].T, **{'color':'k', **kwargs})
def plotpolygons(ax, points, shapes, **kwargs):
    for shape in shapes:
        for vi in zip(shape, np.roll(shape, 1)):
            ax.plot(*points[vi,:].T, **{'color':'b', **kwargs})

if __name__ == '__main__':
    n = 20
    points = np.random.rand(n*2).reshape(-1, 2)

    
    fig, axes = plt.subplots(2, 3,  figsize=(19, 12))
    for i, j in np.ndindex(axes.shape):
        ax = axes[i, j]
        if i==j==0: continue
        kwargs = {'alpha': 0.2, 'linestyle': '-'} if i == 1 else {}
        plotdelaunay(ax, points, **kwargs)
    axes[0,0].set_title('original points')
    axes[0,1].set_title('Delaunay grid')
    axes[0,2].set_title('removable walls')
    plotremovablewalls(axes[0,2], points, color='red')
    axes[1,0].set_title('removed shortest walls first')
    plotpolygons(axes[1,0], points, polygonate(points, 'short'), color='b')
    axes[1,1].set_title('removed longest walls first')
    plotpolygons(axes[1,1], points, polygonate(points, 'long'), color='b')
    axes[1,2].set_title('removed most acute angle first')
    plotpolygons(axes[1,2], points, polygonate(points, 'sharp'), color='b')
    
    for i, j in np.ndindex(axes.shape):
        ax = axes[i, j]
        plotpoints(ax, points)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)