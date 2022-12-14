#!/usr/bin/env python3
#objetivo: Filtra la imagen con el filtro deSavitzky Golay. crea el pearson y rmse
#autor: Quasar 
#fecha: marzo 2022
#version: V1. 

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os, sys
#import gdal, osr
import scipy.stats as st
from osgeo import gdal
from osgeo import osr

# Global variables
progress:int = 0
out_file = None
saving:bool = False
start:bool = False

# Load and save raster files
def loadRasterImage(path):
    """ 
    Load a raster image from disk to memory
    Args:
        path (str): Path to file

    Returns:
        (Dataset GDAL object): Object that contains the structure of the raster file
        (array): Image in array format
        (boolean): Indicates that if there is an error
        (str): Indicates the associated error message
    """
    raster_ds = gdal.Open(path, gdal.GA_ReadOnly)
    if raster_ds is None:
        return None, None, True, "The file cannot be opened."
    print("Driver: ", raster_ds.GetDriver().ShortName, '/', raster_ds.GetDriver().LongName)
    print("Size: ({}, {}, {})".format(raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount))
    if raster_ds.RasterCount == 1:
        return raster_ds, raster_ds.GetRasterBand(1).ReadAsArray(), False, ""
    else:
        return raster_ds, np.stack([raster_ds.GetRasterBand(i).ReadAsArray() for i in range(1, raster_ds.RasterCount+1)], axis=2), False, ""
    
def saveSingleBand(dst, rt, img, tt=gdal.GDT_Int16, typ='GTiff'): ##
    """
    Save a raster image from memory to disk

    Args:
        dst (str): Path to output file
        rt  (Dataset GDAL object): Object that contains the structure of the raster file
        img (array): Image in array format
        tt  (GDAL type, optional): Defaults to gdal.GDT_Float32. Type in which the array is to be saved.
        typ (str, optional): Defaults to 'GTiff'. Driver used to save.
    """
    transform = rt.GetGeoTransform()
    geotiff = gdal.GetDriverByName(typ)
    output = geotiff.Create(dst, rt.RasterXSize, rt.RasterYSize, 1,tt)
    wkt = rt.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    output.GetRasterBand(1).WriteArray(img)
    output.GetRasterBand(1).SetNoDataValue(-999)
    output.SetGeoTransform(transform)
    output.SetProjection(srs.ExportToWkt())
    output = None
    
    
def saveBand(dst, rt, img, tt=gdal.GDT_Int16, typ='GTiff', nodata=-999):##
    """
    Save a raster image from memory to disk

    Args:
        dst (str): Path to output file
        rt  (Dataset GDAL object): Object that contains the structure of the raster file
        img (array): Image in array format
        tt  (GDAL type, optional): Defaults to gdal.GDT_Float32. Type in which the array is to be saved.
        typ (str, optional): Defaults to 'GTiff'. Driver used to save.
    """
    xsize, ysize, zsize = rt.RasterXSize, rt.RasterYSize, rt.RasterCount
    transform = rt.GetGeoTransform()
    geotiff = gdal.GetDriverByName(typ)
    output = geotiff.Create(dst, xsize, ysize, zsize, tt)
    wkt = rt.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    
    for i in range(1, zsize+1): ##
        output.GetRasterBand(i).WriteArray(img[:, :, i-1])##
        output.GetRasterBand(i).SetNoDataValue(nodata)
    
    output.SetGeoTransform(transform)
    output.SetProjection(srs.ExportToWkt())
    output = None

def s(x, meanx, n):##
    return np.sqrt(np.sum(np.power(x, 2)) / n - meanx**2)

def r(x, y):##
    # meanx, meany = np.mean(x), np.mean(y)
    # return ((np.sum(x * y) / len(x)) - (np.mean(x) * np.mean(y))) / (np.std(x)*np.std(y))
    # return ((np.sum(x * y) / n) - (meanx * meany)) / (s(x, meanx, n) * s(y, meany, n))
    return np.corrcoef(x, y)[0, 1]

def rmse(x, y):##
    return np.sqrt(np.mean(np.power(x - y, 2)))

# Main
def getFiltRaster(path:str, window_size:int, polyorder:int):
    """
    Method to filter a raster image with the Savitzky Golay filter

    Args:
        path (str): Path to file
        window_size (int): Window size
        polyorder (int): Polynomial order
    """
    global progress, out_file, saving, start
    progress = 0
    saving = False

    name, ext = os.path.splitext(path)
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)

    # Auxiliar
    aux = np.zeros(img.shape)
    
    # Dims
    height, width, depth = img.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##
    # Run by depth
    
    start = True
    for i in range(height):
        for j in range(width):
            aux[i, j, :] = scipy.signal.savgol_filter(img[i, j, :], window_size, polyorder, deriv=0) #cambiar el tamaño de ventana y polinomio
            rmse[i, j] = np.sqrt(np.sum(np.power(img[i, j, :] - aux[i, j, :], 2))/depth)##
            pearson[i, j] = r(img[i, j, :], aux[i, j, :])     ##   
            progress = int((i * width + j) / (height * width) * 100)
    progress = 100

    # Save  
    saving = True
    dst = f'{name}_SG_{ext}'
    out_file = dst
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_SGrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse, tt=gdal.GDT_Float32)##
    dst = f'{name}_SGpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson, tt=gdal.GDT_Float32)##
    saving = False
    

   
def main():
    path = "x"
    window_size = 7
    polyorder = 2
    getFiltRaster(path, window_size, polyorder)

if __name__ == "__main__":
    main()