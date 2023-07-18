import os, sys
from osgeo import gdal, osr
import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm.contrib import itertools

# global variables
progress:int = 0
out_file:str = ""
saving:bool = False
start:bool = False
out_array:np.ndarray = None

rt = None

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
    global rt
    raster_ds = gdal.Open(path, gdal.GA_ReadOnly)
    if raster_ds is None:
        return None, None, True, "The file cannot be opened."
    print("Driver: ", raster_ds.GetDriver().ShortName, '/', raster_ds.GetDriver().LongName)
    print("Size: ({}, {}, {})".format(raster_ds.RasterXSize, raster_ds.RasterYSize, raster_ds.RasterCount))
    if raster_ds.RasterCount == 1:
        rt = raster_ds
        return raster_ds, raster_ds.GetRasterBand(1).ReadAsArray(), False, ""
    else:
        rt = raster_ds
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
    geotiff = rt.GetDriver()
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
    geotiff = rt.GetDriver()
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

def r(x, y, n):##
    meanx, meany = np.mean(x), np.mean(y)
    return ((np.sum(x * y) / n) - (meanx * meany)) / (s(x, meanx, n) * s(y, meany, n))

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

    # Auxiliar
    aux = np.zeros(img.shape)

    # Dims
    height, width, depth = img.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##

    # Init pandas
    df = pd.DataFrame(columns=['NDVI'])

    # Run by depth
    cont = 0
    start = True
    for i, j in itertools.product(range(height), range(width)):
            aux[i, j, :] = filtFinal(pd.DataFrame(columns=['NDVI'],  data=img[i, j, :]))
            rmse[i, j] = np.sqrt(np.sum(np.power(img[i, j, :] - aux[i, j, :], 2))/depth)##
            pearson[i, j] = st.pearsonr(img[i, j, :], aux[i, j, :])[0]##
            progress = int((i*width + j) * 100 / (height*width))
    progress = 100
            
    # Save
    saving = True
    dst = name + '_max' + ext
    out_file = dst
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_maxrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_maxpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    
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

    # Auxiliar
    aux = np.zeros(array.shape)

    # Dims
    height, width, depth = array.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##

    # Init pandas
    df = pd.DataFrame(columns=['NDVI'])

    # Run by depth
    cont = 0
    start = True
    for i, j in itertools.product(range(height), range(width)):
            aux[i, j, :] = filtFinal(pd.DataFrame(columns=['NDVI'],  data=array[i, j, :]))
            rmse[i, j] = np.sqrt(np.sum(np.power(array[i, j, :] - aux[i, j, :], 2))/depth)##
            pearson[i, j] = st.pearsonr(array[i, j, :], aux[i, j, :])[0]##
            progress = int((i*width + j) * 100 / (height*width))
    progress = 100
            
    # Save
    saving = True
    dst = name + '_max' + ext
    out_file = dst
    out_array = aux
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_maxrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_maxpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    rt= raster
    
def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {__name__} <raster>")
        sys.exit(1)
    path = sys.argv[1]
    getFiltRaster(path)


if __name__ == "__main__":
    main()