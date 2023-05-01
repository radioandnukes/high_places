#!/usr/bin/python3
import argparse
import numpy as np
from simplekml import Kml
from scipy.ndimage import maximum_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to find high spots using 1deg x 1deg SRTM data.')
    parser.add_argument('input_filename', help='SRTM File in .hgt format')
    parser.add_argument('--box_x', type=int, default=300, help='Sets the footprint of the local maximum box. Small numbers = more high points.')
    parser.add_argument('--box_y', type=int, default=300, help='Sets the footprint of the local maximum box. Small numbers = more high points.')
    parser.add_argument('--color_map', default='rainbow', help='Sets the color map of the terrain map')
    parser.add_argument('--print_list', action='store_true', help='Use this to toggle printing the list of high points to the command line')
    parser.add_argument('--freedom_units', action='store_true', help='Use freedom (Imperical) units feet for elevation')
    return parser.parse_args()

def load_elevation_data(filename):
    elevations = np.fromfile(filename, np.dtype('>i2')).reshape((3601, 3601))
    elevations = elevations.astype(float)
    return elevations

def find_local_maxima(elevations, box_x, box_y):
    footprint = np.ones((box_x, box_y))
    local_max = (maximum_filter(elevations, footprint=footprint) == elevations) & (elevations > 0)
    max_indices = np.argwhere(local_max)
    return max_indices

def save_terrain_map(elevations, color_map, image_filename):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(elevations, cmap=color_map, vmin=elevations.min(), vmax=elevations.max())
    plt.axis('off')
    plt.savefig(image_filename, bbox_inches='tight', pad_inches=0, dpi=300)
    plt.close()

def create_kml(elevations, max_indices, image_filename, kml_filename, lat0, lon0, freedom_units, print_list):
    kml = Kml()
    ground = kml.newgroundoverlay(name='Elevation Data')
    ground.icon.href = image_filename
    ground.gxlatlonquad.coords = [(lon0, lat0), (lon0 + 1, lat0), (lon0 + 1, lat0 + 1), (lon0, lat0 + 1)]

    grid_step = 1 / 3600
    lat0_flipped = lat0 + 1

    for index in max_indices:
        row, col = index
        elevation = elevations[row, col]
        if freedom_units:
            elevation = elevation * 3.28
        lat = lat0_flipped - row * grid_step
        lon = lon0 + col * grid_step
        if print_list:
            print(f'{lat:.4f}, {lon:.4f}, {elevation:.0f}')
        kml.newpoint(name=f'{elevation:.0f}{"ft" if freedom_units else "m"}', coords=[
