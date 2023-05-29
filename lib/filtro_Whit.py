#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 19:27:47 2022

@author: ASUS
"""


import os, sys
#import gdal, osr
import numpy as np
import scipy.signal
import scipy.sparse as sparse
from scipy.sparse.linalg import splu
import scipy.stats as st
from osgeo import gdal
from osgeo import osr 
from tqdm.contrib import itertools


def speyediff(N, d, format='csc'):
    """
    (utility function)
    Construct a d-th order sparse difference matrix based on 
    an initial N x N identity matrix
    
    Final matrix (N-d) x N
    """
    
    assert not (d < 0), "d must be non negative"
    shape     = (N-d, N)
    diagonals = np.zeros(2*d + 1)
    diagonals[d] = 1.
    for i in range(d):
        diff = diagonals[:-1] - diagonals[1:]
        diagonals = diff
    offsets = np.arange(d+1)
    spmat = sparse.diags(diagonals, offsets, shape, format=format)
    return spmat


def whittaker_smooth(y, lmbd, d = 2):
    """
    Implementation of the Whittaker smoothing algorithm,
    based on the work by Eilers [1].
    [1] P. H. C. Eilers, "A perfect smoother", Anal. Chem. 2003, (75), 3631-3636
    
    The larger 'lmbd', the smoother the data.
    For smoothing of a complete data series, sampled at equal intervals
    This implementation uses sparse matrices enabling high-speed processing
    of large input vectors
    
    ---------
    
    Arguments :
    
    y       : vector containing raw data
    lmbd    : parameter for the smoothing algorithm (roughness penalty)
    d       : order of the smoothing 
    
    ---------
    Returns :
    
    z       : vector of the smoothed data.
    """

    m = len(y)
    E = sparse.eye(m, format='csc')
    D = speyediff(m, d, format='csc')
    coefmat = E + lmbd * D.conj().T.dot(D)
    z = splu(coefmat).solve(y)
    return z  

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
 

# Main
def getFiltRaster(path):
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
    lmbd = int(depth * 0.1) # 10% of the depth
    print("Lambda: ", lmbd)
    for i, j in itertools.product(range(height), range(width)):
        aux[i, j, :] = whittaker_smooth(img[i, j, :], lmbd, d=2)
        rmse[i, j] = np.sqrt(np.sum(np.power(img[i, j, :] - aux[i, j, :], 2))/depth)##
        pearson[i, j] = st.pearsonr(img[i, j, :], aux[i, j, :])[0]  
    # Save

    dst = f'{name}_whitf_{ext}'
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_whitrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_whitpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    
    
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path to raster>")
        sys.exit(1)
    
    path = sys.argv[1]    
    getFiltRaster(path)