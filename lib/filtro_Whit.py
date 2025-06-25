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
from lib.load_save_raster import loadRasterImage, saveBand, saveSingleBand
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

#  global variables
progress:int = 0
out_file:str = ""
saving:bool = False
start:bool = False
out_array:np.ndarray = None

rt = None


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


def process_row(args):
    i, row, lmbd = args
    rmse_row = np.zeros(row.shape[0])
    pearson_row = np.zeros(row.shape[0])
    for j in range(row.shape[0]):
        aux = np.array(whittaker_smooth(row[j, :], lmbd, d=2)).astype(np.int16)
        rmse_row[j] = np.sqrt(np.sum(np.power(row[j, :] - aux, 2)) / row.shape[1])
        pearson_row[j] = st.pearsonr(row[j, :], aux)[0]
        row[j, :] = aux
    return i, row, rmse_row, pearson_row

    

def getFilter(array:np.array, path:str, raster):
    """Apply Whittaker filter to an array

    Args:
        array (np.array): Matrix to be filtered
        path (str): Path to output file
        raster (gdalDataSet): Raster object
    """
    
    global progress, out_file, saving, start, rt, out_array
    progress = 0
    saving = False
    
    name, ext = os.path.splitext(path)
    
    # Process
    height, width, depth = array.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##
    lmbd = int(depth * 0.1) # 10% of the depth
    print("Lambda: ", lmbd)
    
    start = True
    rows = [(i, array[i, :, :], lmbd) for i in range(height)]
    progress = 0
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row, row_rmse, row_pearson in tqdm(executor.map(process_row, rows), total=height, desc="Filtering with Whittaker"):
            array[i, :, :] = row.astype(np.int16)
            rmse[i, :] = row_rmse
            pearson[i, :] = row_pearson
            progress = int((i + 1) / height * 100)
    progress = 100
    
    saving = True
    dst = f'{name}_whitf_{ext}'
    out_file = dst
    out_array = array
    print("Saving in ", dst)
    saveBand(dst, rt, array)
    dst = f'{name}_whitrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_whitpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    rt = raster
    
# Main
def getFiltRaster(path):
    """
    Apply Whittaker filter to a raster image
    
    Args:
        path (str): Path to file
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

    getFilter(img, path, rt)
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path to raster>")
        sys.exit(1)
    
    path = sys.argv[1]    
    getFiltRaster(path)