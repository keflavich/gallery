"""
An example using the SpectralCube + yt quick-look toolkit to make some
visualizations of R Sculptoris
"""
from __future__ import print_function
from spectral_cube import SpectralCube

# Load the cube data file
# (this can be downloaded from the ALMA archive)
cube = SpectralCube.read('Proj_131_Band3_CO.fits')

# Cut out the signal-rich region of the cube
scube = cube[11:38,172:260,172:260]

# We can look at what it contains:
# SpectralCube with shape=(27, 88, 88):
# n_x: 88  type_x: RA---SIN  unit_x: deg
# n_y: 88  type_y: DEC--SIN  unit_y: deg
# n_s: 27  type_s: FREQ      unit_s: Hz

# Create a yt dataset/data cube from this object
# Choose spectral_factor=3 to increase the spectral axis from 27 to 81
# (which makes the rendering more symmetric)
ytc = scube.to_yt(spectral_factor=3)

# Create a quick-look visualization using only the defaults
# This takes ~30s on a 2014 Macbook Pro
# Note that the movie generation requires ffmpeg (http://ffmpegmac.net/,
# https://www.ffmpeg.org/download.html)
image_list_defaults = ytc.quick_render_movie('RScl_QuickRenderMovie_Defaults')

# You can view the file: it will be called
# 'RScl_QuickRenderMovie_Defaults/out.mp4'
# It is also available here: https://vimeo.com/104692959

# We can tweak the defaults to make a more interesting image
# We'll first determine the noise in the image, approximately
# (1) Identify the bright regions:
sumproj = cube.sum(axis=0)
# Have a look at the image
sumproj.quicklook()

# Make a mask from this projection, selecting the signal-free regions
from spectral_cube import BooleanArrayMask
noisemask = BooleanArrayMask(sumproj < 1, cube.wcs, shape=cube.shape)

# Create the masked noise cube
noisecube = cube.with_mask(noisemask)
# Compute the noise
noise = noisecube.std()
print("1-sigma Noise level: ",noise)

# Also, compute the max of the signal cube:
print("Signal peak: ", scube.max())

# Now create a new transfer function
# We'll use 3-sigma as our noise floor for the visualization
tfh = ytc.auto_transfer_function([3*noise,scube.max()])
# The transfer function helper adds a bunch of independent layers...
# It's not the easiest thing to understand, but there is lots of help at
# http://yt-project.org/docs/3.0/visualizing/volume_rendering.html#transfer-functions
tfh.tf.add_layers(15, colormap='hsv')

# You can also have a look at the transfer function directly
tfh.plot('transfer_function.png')

# Then, let's do the projection again: this time, bigger!
# (because of the larger size and greater # of frames, this takes ~5-10x
# longer, ~3-5 minutes)
image_list_custom = ytc.quick_render_movie('RScl_QuickRender_HSV',
                                           transfer_function=tfh.tf,
                                           nframes=60, size=512)
