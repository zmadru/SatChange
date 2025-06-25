import os, sys
from osgeo import gdal, osr
import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm.contrib import itertools
from lib.load_save_raster import loadRasterImage, saveBand, saveSingleBand
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# global variables
progress:int = 0
out_file:str = ""
saving:bool = False
start:bool = False
out_array:np.ndarray = None

rt = None



def filtFinal(df):
    # Max column
    df['cond1'] = df.NDVI <= 0
    df['max'] = 0
    df.loc[df.cond1 == True, 'max'] = df.rolling(3, center=True, min_periods=1)['NDVI'].max()
    df.loc[df.cond1 == False, 'max'] = df.NDVI

    # Umbral column
   
    df['umbral'] = df['max'].rolling(7, center=True).mean()
    df['umbral'] = df['max'].rolling(7, center=True, min_periods=6).mean()
    df['umbral'] = df['max'].rolling(7, center=True, min_periods=5).mean()
    df['umbral'] = df['max'].rolling(7, center=True, min_periods=4).mean()

    # Maxmax column
    df['maxmax'] = df['max'].rolling(7, center=True).max()
    df['maxmax'] = df['max'].rolling(7, center=True, min_periods=6).max()
    df['maxmax'] = df['max'].rolling(7, center=True, min_periods=5).max()
    df['maxmax'] = df['max'].rolling(7, center=True, min_periods=4).max()

    # Filtint columns
    df['cond2'] = df['max'] <= df['umbral']
    df['filtint'] = df['max']
    df.loc[df.cond2 == True, 'filtint'] = df.maxmax

    # Filtfinal columns
   
    df['filtfinal'] = df['filtint'].rolling(7, center=True).mean()
    df['filtfinal'] = df['filtint'].rolling(7, center=True, min_periods=6).mean()
    df['filtfinal'] = df['filtint'].rolling(7, center=True, min_periods=5).mean()
    df['filtfinal'] = df['filtint'].rolling(7, center=True, min_periods=4).mean()
   
        
    return df['filtfinal']


def process_row_max(args):
    i, row = args
    row_rmse = np.zeros(row.shape[0])
    row_pearson = np.zeros(row.shape[0])
    for j in range(row.shape[0]):
        df = pd.DataFrame(columns=['NDVI'], data=row[j, :])
        aux = filtFinal(df).astype(np.int16)
        row_rmse[j] = np.sqrt(np.sum(np.power(row[j, :] - aux, 2)) / row.shape[1])
        row_pearson[j] = st.pearsonr(row[j, :], aux)[0]
        row[j, :] = aux
    return i, row, row_rmse, row_pearson


def getFilter(array:np.array, path:str, raster):
    """
    Method that applies the filter to an array with the Max method
    
    Args:
        array (np.array): Array to apply the filter
        path (str): Path to input file
        raster (Dataset GDAL object): Object that contains the structure of the raster file
    """
    global progress, out_file, saving, start, rt, out_array
    progress = 0
    saving = False 
    
    name, ext = os.path.splitext(path)

    # Dims
    height, width, depth = array.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##

    # Run by depth
    cont = 0
    start = True
    rows = [(i, array[i,:,:]) for i in range(height)]
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row, row_rmse, row_pearson in tqdm(executor.map(process_row_max, rows), total=height, desc="Filtering with Max"):
            array[i, :, :] = row.astype(np.int16)
            rmse[i, :] = row_rmse
            pearson[i, :] = row_pearson
    progress = 100
            
    # Save
    saving = True
    dst = name + '_max' + ext
    out_file = dst
    out_array = array
    print("Saving in ", dst)
    saveBand(dst, raster, array)
    dst = f'{name}_maxrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, raster, rmse)##
    dst = f'{name}_maxpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, raster, pearson)##
    saving = False
    rt= raster
    

def getFiltRaster(path):
    """
    Method that applies the filter to a raster image with the Max method
    
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
        print(f"Usage: python3 {__name__} <raster>")
        sys.exit(1)
    path = sys.argv[1]
    getFiltRaster(path)


if __name__ == "__main__":
    main()