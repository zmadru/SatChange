import os, sys
import threading
from osgeo import gdal
from osgeo import osr
#import gdal, osr
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy.ndimage.filters import maximum_filter1d
import scipy.signal
import scipy.stats as st
import statsmodels.tsa.stattools as pc
from tqdm.contrib import itertools
from lib.load_save_raster import loadRasterImage, saveBand, saveSingleBand
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import gc

# Global variables
progress:int = 0
out_file:str = ''
saving:bool = False
start:bool = False
out_array:np.ndarray = None
img = None
rt = None 

def process_row_acf(args):
    i, row, nlags = args
    w = row.shape[0]  # width of the row
    # aux_row = np.zeros(nlags + 1).astype(np.int16)
    aux_row = np.zeros((w, nlags + 1), dtype=np.int16)  # Initialize the row for ACF values
    for j in range(w):
        acf_values = pc.acf(row[j, :], nlags=nlags, alpha=0.05, fft=False)[0] * 10000
        aux_row[j, :] = np.array(acf_values).astype(np.int16)  # Store ACF values for each pixel
    return i, aux_row


def ac(array:np.ndarray, path:str, raster, nlags_:int=364):
    """Calculate the autocorrelation function of a raster image

    Args:
        array (np.ndarray): Matrix of the raster image
        path (str): Path to the raster image
        raster (_type_): raster to set the output projection
        nlags (int, optional): number of lags. Defaults to 364.
    """
    global progress, out_file, saving, out_array, rt, start, nlags

    nlags = nlags_
    progress = 0
    saving = False
    start = True

    # Read raster
    name, ext = os.path.splitext(path)
    out_file = f'{name}_ACF_L{nlags}{ext}'

    # Process
    height, width, depth = array.shape
    aux = np.zeros((height, width, nlags+1)).astype(np.float32)
    rows = [(i, array[i, :, :], nlags) for i in range(height)]
    del array  # Free memory
    gc.collect()  # Collect garbage
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row_acf in tqdm(executor.map(process_row_acf, rows), total=height, desc="Calculating ACF"):
            aux[i, :, :] = row_acf    
            progress = int((i + 1) / height * 100)
    progress = 100
    
    # Remove the first lag (0), because it is always 1
    # aux = aux[:, :, 1:]
    out_array = aux
    
    # Save
    saving = True
    rt = raster
    print("Saving in ", out_file)
    saveBand(out_file, raster, aux)
    saving = False
    start = False


# Main
def ACFtif(path:str, nlags_:int = 364):
    global progress, out_file, saving, start, nlags
    name, ext = os.path.splitext(path)
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)

    ac(img, path, rt, nlags_=nlags_)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python3 {__file__} <raster> <nlags>")
        sys.exit(1)
        
    path = sys.argv[1]
    nlags = int(sys.argv[2])
    aux3 = ACFtif(path, nlags)