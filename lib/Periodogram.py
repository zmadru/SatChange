import os, sys
#import gdal, osr
import numpy as np
import scipy.signal as sg
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

def process_row_period(args):
    i, row, len_pxx = args
    w = row.shape[0]
    period_row = np.zeros((w, len_pxx)).astype(np.int16)
    for j in range(w):
        # Calculate the periodogram for each pixel
        _, pxx = sg.periodogram(row[j, :])
        period_row[j, :] = np.array(pxx).astype(np.int16)
    return i, period_row


def period(array:np.ndarray, path:str, raster):
    """Calculate the periodogram of a raster array.
    Args:
        array (np.ndarray): 3D numpy array with shape (height, width, depth).
        path (str): Path to the raster file.
        raster: Raster object for saving the output.
    Returns:
        None
    """
    global progress, out_file, saving, out_array, rt, start

    progress = 0
    saving = False
    start = True

    # Read raster
    name, ext = os.path.splitext(path)
    out_file = f'{name}_Periodogram{ext}'

    # Process
    height, width, depth = array.shape
    frqs, pxx = sg.periodogram(array[0, 0, :])
    aux = np.zeros((height, width, pxx.shape[0]))
    rows = [(i, array[i, :, :], len(pxx)) for i in range(height)]
    del array  # Free memory
    gc.collect()  # Collect garbage
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row_period in tqdm(executor.map(process_row_period, rows), total=height, desc="Calculating periodogram", unit="row"):
            aux[i, :, :] = row_period
            progress = int((i + 1) / height * 100)
    progress = 100
    
    out_array = aux
    
    # Save
    saving = True
    rt = raster
    (1/frqs).tofile(f'{name}_Periodogram_freqs.txt', sep='\n')
    print("Saving in ", out_file)
    saveBand(out_file, raster, aux)
    saving = False
    start = False


# Main
def periodtif(path:str):
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)

    period(img, path, rt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {__file__} <raster> ")
        sys.exit(1)
        
    path = sys.argv[1]
    aux3 = periodtif(path)