import os, sys
from osgeo import gdal, osr
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy.ndimage import maximum_filter1d
import os, sys
import scipy.stats as st
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

# FFT filter

def max_filter1d_valid(a, W):
    hW = (W-1)//2
    return maximum_filter1d(a,size=W)[hW:-hW]

def filterFFt1d(sig, threshold=0.05, closest=0):
    # The FFT of the signal
    sig_fft = fftpack.fft(sig)
    # The corresponding frequencies
    sample_freq = fftpack.fftfreq(sig.size)
    power = np.abs(sig_fft)**2
    # Find the peak frequency: we can focus on only the positive frequencies
    peak_freq = sample_freq[sample_freq > threshold][power[sample_freq > threshold].argmax()]
    # Ifft
    sig_fft[np.abs(sample_freq) > peak_freq] = closest
    return fftpack.ifft(sig_fft)


def process_row_fft(args):
    i, row = args
    row_rmse = np.zeros(row.shape[0])
    row_pearson = np.zeros(row.shape[0])
    for j in range(row.shape[0]):
        tt = np.abs(filterFFt1d((np.array(row[j, :])), threshold=0.05))
        aux = np.pad(tt, (0, row.shape[1] - len(tt)), 'constant').astype(np.int16)
        row_rmse[j] = np.sqrt(np.sum(np.power(row[j, :] - aux, 2)) / row.shape[1])
        row_pearson[j] = st.pearsonr(row[j, :], aux)[0]
        row[j, :] = aux
    return i, row, row_rmse, row_pearson


def getFilter(array:np.array, path:str, raster):
    """Generates a filtered array

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
    start = True
    height, width, depth = array.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##
    
    start = True
    rows = [(i, array[i, :, :]) for i in range(height)]
    progress = 0
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row, row_rmse, row_pearson in tqdm(executor.map(process_row_fft, rows), total=height, desc="Filtering with FFT"):
            array[i, :, :] = row.astype(np.int16)
            rmse[i, :] = row_rmse
            pearson[i, :] = row_pearson
            progress = int((i + 1) / height * 100)
    progress = 100
            
    # Save
    saving = True
    dst = f'{name}_FFT_{ext}'
    out_file = dst
    out_array = array
    print("Saving in ", dst)
    saveBand(dst, rt, array)
    dst = f'{name}_fftrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_fftpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    rt = raster


# Main
def getFiltRaster(path):
    """
    Method to filter a raster image with FFT

    Args:
        path (str): Path to input file
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


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {__name__} <path to raster>")
        sys.exit(1)
    getFiltRaster(sys.argv[1])

if __name__ == "__main__":
    main()