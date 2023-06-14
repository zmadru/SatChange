import os, sys
#import gdal, osr
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy.ndimage.filters import maximum_filter1d
from scipy import interpolate
from scipy.interpolate import interp1d
from osgeo import gdal
from osgeo import osr
from tqdm.contrib import itertools

# Global variables
progress:int = 0
out_file = None
saving:bool = False
array:np.ndarray = None
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
    rt = raster_ds
    if raster_ds.RasterCount == 1:
        return raster_ds, raster_ds.GetRasterBand(1).ReadAsArray(), False, ""
    else:
        return raster_ds, np.stack([raster_ds.GetRasterBand(i).ReadAsArray() for i in range(1, raster_ds.RasterCount+1)], axis=2), False, ""
    
    
def saveBand(dst, rt, img, tt=gdal.GDT_Int16, typ='GTiff', nodata=-999):
    """
    Save a raster image from memory to disk

    Args:
        dst (str): Path to output file
        rt  (Dataset GDAL object): Object that contains the structure of the raster file
        img (array): Image in array format
        tt  (GDAL type, optional): Defaults to gdal.GDT_Float32. Type in which the array is to be saved.
        typ (str, optional): Defaults to 'GTiff'. Driver used to save.
    """
    global saving
    saving = True
    xsize, ysize, zsize = rt.RasterXSize, rt.RasterYSize, rt.RasterCount
    transform = rt.GetGeoTransform()
    geotiff = rt.GetDriver()
    output = geotiff.Create(dst, xsize, ysize, zsize, tt)
    wkt = rt.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    
    for i in range(1, zsize+1):
        output.GetRasterBand(i).WriteArray(img[:, :, i-1])
        output.GetRasterBand(i).SetNoDataValue(nodata)
    
    output.SetGeoTransform(transform)
    output.SetProjection(srs.ExportToWkt())
    output = None
    saving = False

def fill(A, value, method):
    '''
    interpolate
    '''
    """"if A[0] == 0:
        for i in range(len(A)):
            if A[i] != 0:
                A[0] = A[i]
                break
     """        
    inds = np.arange(A.shape[0])
    good = np.where(A != value)
    if len(good[0]) >=2 and len(inds) >= 2:
        f = interpolate.interp1d(inds[good], A[good], method, bounds_error =False, fill_value="extrapolate")
        A = np.where(A != value, A, f(inds))           
    return A


# Main
def getFiltRaster(path:str, modeInterp:str='linear', saveformat:str='int16'):
    """Method to filter a raster image

    Args:
        path (str): Path to raster image
        modeInterp (str, optional): Interpolation mode. Defaults to None.
    """
    global progress, out_file, array

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
    print(img.shape)
    # Init pandas
    df = pd.DataFrame(columns=['NDVI'])

    # Run by depth
    
    for i,  j in itertools.product(range(height), range(width)):
        aux[i, j, :] = fill(img[i, j, :], 0, modeInterp)
        progress = (i * width + j) / (height * width) * 100
    
    progress = 100
    # Save
    dst = f'{name}_filt_{modeInterp}_{ext}'
    out_file = dst
    print("Saving in ", dst)
    if saveformat == 'float32':
        array = aux.astype(np.float32)
        saveBand(dst, rt, aux, tt=gdal.GDT_Float32)
    else:
        aux = aux * 10000
        array = aux.astype(np.int16)
        saveBand(dst, rt, aux, tt=gdal.GDT_Int16)
        
    
    


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 interpolacion.py <path> <saveformat>\n<path>: Path to raster image\n <saveformat>: Format to save the raster image(int16, float32)")
        sys.exit(1)
        
    path = sys.argv[1]
    saveformat = sys.argv[2]
    print("Path: ", path)
    getFiltRaster(path, modeInterp='linear',saveformat=saveformat)
    
###en el método de llenado borra todo y deja el que diga 'linear' , es el que mejor se comporta. , 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'