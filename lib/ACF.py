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

# Global variables
progress:int = 0
out_file = None
saving:bool = False
start:bool = False
out_array:np.ndarray = None

rt = None

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
     
def saveSingleBand(dst, rt, img, tt=gdal.GDT_Float32, typ='GTiff'): ##
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
 
        
def saveBand(dst, rt, img, tt=gdal.GDT_Float32, typ='GTiff', nodata=-999):##
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
    zsize += 1
    output = geotiff.Create(dst, xsize, ysize, zsize, tt)
    wkt = rt.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    
    for i in range(img.shape[-1]): ##
        output.GetRasterBand(i+1).WriteArray(img[:, :, i])##
        output.GetRasterBand(i+1).SetNoDataValue(nodata)
    
    output.SetGeoTransform(transform)
    output.SetProjection(srs.ExportToWkt())
    output = None

# Main
img = None
def ACFtif(path:str):
    global progress, out_file, saving
    name, ext = os.path.splitext(path)
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)

    # Auxiliar
    nlags = 364
    height, width, depth = img.shape
    aux = np.zeros((height, width, nlags+1))
    # aux2 = np.zeros((height, width, nlags+1))
        

    # Run by depth
    for i in range(height):
        for j in range(width):
            #print(pc.acf(img[i, j, :], nlags=nlags, alpha=0.05))
            aux[i, j, :] = pc.acf(img[i, j, :], nlags=nlags, alpha=0.05)[0]
            # aux2[i, j, :] = pc.pacf(img[i, j, :], nlags=nlags, method='ywunbiased', alpha=0.05)[0]
            progress = int((i*width+j)/(height*width)*100)
                        
    # Save
    saving = True
    dst = f'{name}_ACF1_{ext}'
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    out_file = dst
    # dst = f'{name}_PACF1_{ext}'
    # print("Saving in ", dst)
    # saveBand(dst, rt, aux2)
    saving = False
    return aux

def ac(array:np.ndarray, path:str, raster, nlags:int=364):
    """Calculate the autocorrelation function of a raster image

    Args:
        array (np.ndarray): Matrix of the raster image
        path (str): Path to the raster image
        raster (_type_): raster to set the output projection
        nlags (int, optional): number of lags. Defaults to 364.
    """
    global progress, out_file, saving, out_array, rt, start
    progress = 0
    saving = False
    start = True

    # Read raster
    name, ext = os.path.splitext(path)

    # Process
    height, width, depth = array.shape
    aux = np.zeros((height, width, nlags+1))
    for i in range(height):
        for j in range(width):
            aux[i, j, :] = pc.acf(array[i, j, :], nlags=nlags, alpha=0.05)[0]
            progress = int((i*width+j)/(height*width)*100)
    
    saving = True
    out_array = aux
    out_file = f'{name}_ACF1_{ext}'
    print("Saving in ", out_file)
    saveBand(out_file, raster, aux)
    rt = raster
    saving = False
    start = False




if __name__ == "__main__":
    path = r'S:\30TUK\Series\T30TUK_NDVI_2016_2021_CLIP2_int_filt_linear__whitf_'
    aux3 = ACFtif(path)