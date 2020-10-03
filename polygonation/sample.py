from polygonation import polygonate as pg 
import numpy as np
from matplotlib import pyplot as plt


# Sample use.
n = 20
points = np.random.rand(n*2).reshape(-1, 2)
polygons = pg.polygonate(points, 'acute', convex=False)
# drawing the result
fig, ax = plt.subplots(1, 1, figsize=(10,10))
pg.plotdelaunay(ax, points, alpha=0.2)
pg.plotpolygons(ax, points, polygons)
pg.plotpoints(ax, points)
ax.set_xticks([])
ax.set_yticks([])


# Comparison.

n = 150
points = np.random.rand(n*2).reshape(-1, 2)

for convex in [True, False]:
    fig, axes = plt.subplots(2, 3,  figsize=(15, 10))
    for i, j in np.ndindex(axes.shape):
        ax = axes[i, j]
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)
        if i==j==0: continue
        kwargs = {'alpha': 0.1} if i > 0 else {}
        pg.plotdelaunay(ax, points, **kwargs)
    fig.suptitle(f'Polygons must be convex: {convex}')
    axes[0,0].set_title('points')
    pg.plotpoints(axes[0,0], points)
    axes[0,1].set_title('Delaunay grid')
    axes[0,2].set_title('removable walls')
    pg.plotremovablewalls(axes[0,2], points, color='r', convex=convex)
    axes[1,0].set_title('remove longest walls first')
    pg.plotpolygons(axes[1,0], points, pg.polygonate(points, 'long', convex=convex), color='b')
    axes[1,1].set_title('remove acute angles first')
    pg.plotpolygons(axes[1,1], points, pg.polygonate(points, 'acute', convex=convex), color='b')
    axes[1,2].set_title('remove wall that produces roundest polygon')
    pg.plotpolygons(axes[1,2], points, pg.polygonate(points, 'round', convex=convex), color='b')
    
    fig.tight_layout()
