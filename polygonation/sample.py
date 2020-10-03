from polygonation.polygonate import Polygonate
import numpy as np
from matplotlib import pyplot as plt


# Sample use.

# calculating the polygons
n = 20
points = np.random.rand(n*2).reshape(-1, 2)
pg = Polygonate(points)
# drawing the result
fig, ax = plt.subplots(1, 1, figsize=(10,10))
pg.plotdelaunay(ax, alpha=0.2)
pg.plotpolygons(ax)
pg.plotpoints(ax)
ax.set_xticks([])
ax.set_yticks([])


# Comparison.

n = 10
points = np.random.rand(n*2).reshape(-1, 2)

for convex in [True, False]:
    pg = Polygonate(points, 'long', convex=convex)
    
    fig, axes = plt.subplots(2, 3,  figsize=(15, 10))
    for i, j in np.ndindex(axes.shape):
        ax = axes[i, j]
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)
        if i==j==0: continue
        kwargs = {'alpha': 0.1} if i > 0 else {}
        pg.plotdelaunay(ax, **kwargs)
    fig.suptitle(f'Polygons must be convex: {convex}')
    axes[0,0].set_title('points')
    pg.plotpoints(axes[0,0])
    axes[0,1].set_title('Delaunay grid')
    axes[0,2].set_title('removable walls')
    pg.plotremovablewalls(axes[0,2], color='r')
    axes[1,0].set_title('remove longest walls first')
    pg.plotpolygons(axes[1,0], color='b')
    axes[1,1].set_title('remove acute angles first')
    Polygonate(points, 'acute', convex=convex).plotpolygons(axes[1,1], color='b')
    axes[1,2].set_title('remove wall that produces roundest polygon')
    Polygonate(points, 'round', convex=convex).plotpolygons(axes[1,2], color='b')
    
    fig.tight_layout()
