import os, sys
from osgeo import gdal, osr
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy.ndimage import maximum_filter1d
import os, sys
import scipy.stats as st
from tqdm.contrib import itertools

# Global variables
progress:int = 0
out_file:str = ""
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

    # Auxiliar
    aux = np.zeros(img.shape)

    # Dims
    height, width, depth = img.shape
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##

    # Init pandas
    df = pd.DataFrame(columns=['NDVI'])

    # Run by depth
    start = True
    for i, j in itertools.product(range(height), range(width)):
            #aux[i, j, :] = np.abs(filterFFt1d(img[i, j, :], threshold=0.05)
            tt = np.abs(filterFFt1d((np.array(img[i, j, :])), threshold=0.05))
            #tt = np.abs(filterFFt1d(max_filter1d_valid(np.array(img[i, j, :]), 3), threshold=0.05))
            aux[i, j, :] = np.pad(tt, (0, depth - len(tt)), 'constant')
            rmse[i, j] = np.sqrt(np.sum(np.power(img[i, j, :] - aux[i, j, :], 2))/depth)##
            pearson[i, j] = st.pearsonr(img[i, j, :], aux[i, j, :])[0]##  
            progress = int((i*width + j)/(height*width) * 100)   
    progress = 100
            
    # Save
    saving = True
    dst = f'{name}_FFT_{ext}'
    out_file = dst
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_fftrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_fftpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    return aux

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
    height, width, depth = array.shapeheight, width, depth = array.shape
    aux = np.zeros(array.shape)
    rmse = np.zeros((height, width))##
    pearson = np.zeros((height, width))##
    
    start = True
    for i, j in itertools.product(range(height), range(width)):
            tt = np.abs(filterFFt1d((np.array(array[i, j, :])), threshold=0.05))
            aux[i, j, :] = np.pad(tt, (0, depth - len(tt)), 'constant')
            rmse[i, j] = np.sqrt(np.sum(np.power(array[i, j, :] - aux[i, j, :], 2))/depth)##
            pearson[i, j] = st.pearsonr(array[i, j, :], aux[i, j, :])[0]##  
            progress = int((i*width + j)/(height*width) * 100)   
    progress = 100
            
    # Save
    saving = True
    dst = f'{name}_FFT_{ext}'
    out_file = dst
    out_array = aux
    print("Saving in ", dst)
    saveBand(dst, rt, aux)
    dst = f'{name}_fftrmse_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, rmse)##
    dst = f'{name}_fftpearson_{ext}'
    print("Saving in ", dst)
    saveSingleBand(dst, rt, pearson)##
    saving = False
    rt = raster

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {__name__} <path to raster>")
        sys.exit(1)
    getFiltRaster(sys.argv[1])

if __name__ == "__main__":
    main()