#!/usr/bin/python3
##################################################################
# Tool to find high spots using 1deg x 1deg SRTM data
#
# The script will output a KML and a PNG file.
# The KML will display the terrain map with local maximum points
#
# Requirments = numpy, scipy, matplotlib, simplekml
#
# Source for SRTM data https://dwtkns.com/srtm30m/
#
#
###################################################################

import numpy as np
from simplekml import Kml
from scipy.ndimage import maximum_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import sys

# Sets the footprint of the local maximum box. Small numbers = more high points.
box_x = 300
box_y = 300

# Sets the color map of the terrain map
# See https://matplotlib.org/stable/tutorials/colors/colormaps.html
color_map = 'rainbow'

# I/O options
auto_name = True # Use this to automaticly name the output files based on input_filename

input_filename = 'N38W095.hgt' # ONLY USED IF auto_name=False SRTM File in .hgt format
## Note the output png and kml files will be auto named based on the input filename

print_list = False # Use this to toggle printing the list of high points to the command line

freedom_units = True # Use freedom (Imperical) units feet for elevation

###########################################################################################
###########################################################################################

# Each point in the 3600x3600 array = 1 deg / 3600 = 2.777777777777778e-4 deg
grid_step = 1/3600

# Filename as command line argument systax check
if len(sys.argv[1]) == 11:
	if sys.argv[1][0] == 'N' or sys.argv[1][0] == 'S':
		if  sys.argv[1][3] == 'E' or sys.argv[1][3] == 'W':
			input_filename = sys.argv[1]
		else:
			print('Filename failed syntax check')
			quit()

# IMPORTANT the filename must be in N55E013.hgt repersenting North / South, 2 Digit Latitude in degrees, East / West, 3 Digit Longitude in degrees
print('Filename = %s converted to Lat = %d, Lon = %d' % (input_filename, int(input_filename[1:3]), int(input_filename[4:7])))

lat0 = int(input_filename[1:3])
lon0 = int(input_filename[4:7])

# North or South of equator, East or West of prime meridian
if input_filename[0] == 'N':
    print('North Positive Lat')

if input_filename[0] == 'S':
    print('South Negitive Lat')
    lat0 = -abs(lat0)

if input_filename[3] == 'E':
    print('East Positive Lon')

if input_filename[3] == 'W':
    print('East Negitive Lon')
    lon0 = -abs(lon0)

# Auto names output files if auto_name is True
image_filename = '%s.png' % (input_filename[0:7])
kml_filename = '%s.kml' % (input_filename[0:7])

# add 1 to lat0 due to hgt file origin being bottom left vs top right.
lat0_flipped = lat0 + 1

# Load elevation data
#elevations = np.loadtxt('N55E013.hgt', dtype='int16', skiprows=0)
elevations = np.fromfile(input_filename, np.dtype('>i2')).reshape((3601, 3601))
elevations = elevations.astype(float)

# Find local maxima using maximum_filter
footprint = np.ones((box_x, box_y))
local_max = (maximum_filter(elevations, footprint=footprint) == elevations) & (elevations > 0)

# Get indices of local maxima
max_indices = np.argwhere(local_max)

# Create a KML document
kml = Kml()

# Print number of hight points found
print('Found %d high points' % (len(max_indices)))

# generate terrain map you can change the color map
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(elevations, cmap=color_map, vmin=elevations.min(), vmax=elevations.max())
plt.axis('off')
plt.savefig(image_filename, bbox_inches='tight', pad_inches=0, dpi=300)
plt.close()

print('Terrain map saved as %s' % (image_filename))

print('KML saved as %s' % (kml_filename))

# Generate the KML file
ground = kml.newgroundoverlay(name='Elevation Data')
ground.icon.href = image_filename
ground.gxlatlonquad.coords = [(lon0, lat0), (lon0 + 1, lat0), (lon0 + 1, lat0 + 1), (lon0, lat0 + 1)]

if print_list == True:
	print('Lat, Lon, Elevation (m)')
	if freedom_units == True:
		print('Lat, Lon, Elevation (Ft)')

# Loop over indices and print corresponding elevation values
for index in max_indices:
	row, col = index
	elevation = elevations[row, col]
	if freedom_units == True:
		elevation = elevation * 3.28
	lat = lat0_flipped - row * grid_step
	lon = lon0 + col * grid_step
	### Uncomment the next line for a verbose output
	if print_list == True:
		print('%1.4f, %1.4f, %d' % (lat, lon, elevation))
	if freedom_units == False:
		kml.newpoint(name=f'%dm' % (elevation), coords=[(lon, lat, elevation)])
	if freedom_units == True:
		kml.newpoint(name=f'%dft' % (elevation), coords=[(lon, lat, elevation)])

kml.save(kml_filename)
