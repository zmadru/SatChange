#!/usr/bin/env python3
#objetivo: Filtra la imagen con el filtro deSavitzky Golay. crea el pearson y rmse
#autor: Quasar & Diego Madruga
#fecha: febrero 2023
#version: V2. 

import threading
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os, sys
#import gdal, osr
import scipy.stats as st
from osgeo import gdal
from osgeo import osr
from tqdm.contrib import itertools
from lib.load_save_raster import loadRasterImage, saveBand, saveSingleBand
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# Global variables
progress:int = 0
out_file:str = ""
saving:bool = False
start:bool = False
out_array:np.ndarray = None
rt = None


def process_row_sg(args):
    i, row, window_size, polyorder = args
    rmse_row = np.zeros(row.shape[0])
    pearson_row = np.zeros(row.shape[0])
    
    for j in range(row.shape[0]):
        aux = np.array(scipy.signal.savgol_filter(row[j, :], window_size, polyorder, deriv=0)).astype(np.int16)
        rmse_row[j] = np.sqrt(np.sum(np.power(row[j, :] - aux, 2)) / row.shape[1])
        pearson_row[j] = st.pearsonr(row[j, :], aux)[0]
        row[j, :] = aux
    return i, row, rmse_row, pearson_row


def getFilter(array:np.ndarray, window_size:int, polyorder:int, path:str, raster):
    """Generates a filtered array

    Args:
        array (np.ndarray): Matrix to be filtered
        window_size (int): Window size
        polyorder (int): Polynomial order
        path (str): Path to save the filtered array
    """
    global progress, out_file, saving, start, out_array, rt
    progress = 0
    saving = False

    name, ext = os.path.splitext(path)

    # Process
    start = True
    height, width, depth = array.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##
    rows = [(i, array[i, :, :], window_size, polyorder) for i in range(height)]
    progress = 0
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row, row_rmse, row_pearson in tqdm(executor.map(process_row_sg, rows), total=height, desc="Filtering with Savitzky Golay"):
            array[i, :, :] = row.astype(np.int16)
            rmse[i, :] = row_rmse
            pearson[i, :] = row_pearson
            progress = int((i + 1) / height * 100) 

    progress = 100

    # Save
    saving = True   
    dst = f'{name}_SG_{ext}'
    out_file = dst
    out_array = array
    print("Saving in ", dst)
    saveBand(dst, raster, array)
    dst = f'{name}_SGrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, raster, rmse, tt=gdal.GDT_Float32)##
    dst = f'{name}_SGpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, raster, pearson, tt=gdal.GDT_Float32)##
    rt = raster
    saving = False


# Main
def getFiltRaster(path:str, window_size:int, polyorder:int):
    """
    Method to filter a raster image with the Savitzky Golay filter

    Args:
        path (str): Path to file
        window_size (int): Window size
        polyorder (int): Polynomial order
    """
    global progress, out_file, saving, start, rt
    progress = 0
    saving = False

    name, ext = os.path.splitext(path)
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)
        
    getFilter(img, window_size, polyorder, path, rt)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} <path> <window_size> <polyorder>")
        sys.exit(1)
    path = sys.argv[1]
    window_size = int(sys.argv[2])
    polyorder = int(sys.argv[3])
    getFiltRaster(path, window_size, polyorder)

if __name__ == "__main__":
    main()