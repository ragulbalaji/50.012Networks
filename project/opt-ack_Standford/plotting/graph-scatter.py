#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

FNAME = "10.0.0.2.csv"
INTERVAL = 33 # How often to refresh the plot, in ms
FPS = 30
plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'

# Get the points in advance
pts = []
with open(FNAME) as f:
    for line in f:
        x,y = line.split(',')
        pts.append((float(x), float(y)))
pts.sort()

blocks = []
curBlock = []
i = 1
for pt in pts:
    while pt[0] > i * (INTERVAL/1000.0):
        blocks.append(curBlock)
        curBlock = []
        i += 1
    curBlock.append(pt)
blocks.append(curBlock)

# Set up the figure and the axes
fig = plt.figure()
ax = fig.add_subplot(1,1,1)

# animation function.  This is called sequentially
def animate(i, blocks):
    if blocks[i]:
        xs, ys = zip(*blocks[i])
        ax.scatter(xs, ys)
        ax.set_ylim([0,ys[-1]])
    ax.set_xlim([0,i*(INTERVAL/1000.0)])

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, frames=len(blocks), interval=200,
        fargs=(blocks,), repeat=False, blit=False)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
anim.save('basic_animation.mp4', fps=FPS)

plt.show()

"""
Sources:

1.

Matplotlib Animation Example
author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD

2.

http://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow

"""
