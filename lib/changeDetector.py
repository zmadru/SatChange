import os, sys
from osgeo import gdal
from osgeo import osr
#import gdal, osr
import numpy as np
import threading

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


def checkPixel(i, j, array, length):
    """Check the time serie from a pixel to see if there are an average of 50% of positive and negative values
    
    Args:
        i (int): Row
        j (int): Column
        array (np.ndarray): Time serie of the pixel
        length (int): Length of the time serie
    """
    global mask, progress

    positives, negatives = 0, 0
    for k in range(length):
        if array[k] > 0:
            positives += 1
        else:
            negatives += 1

    # If the average of the positive and negatives values is near to fifty (40, 60), the pixel is not considered as a change
    if positives/length < 0.4 or negatives/length < 0.4:
        mask[i, j] = 1
    
    progress += 1
        
    


def changeDetector(array:np.ndarray, path:str, raster):
    """Calculate the change detector of an array given an array
    
    Args:
        array (np.ndarray): Matrix of the raster image autocorrelation
        path (str): Path to the raster image
    """
    global progress, out_file, saving, out_array, start, mask

    progress = 0
    saving = False
    start = True

    # Read raster
    height, width = array.shape[:2]
    name, ext = os.path.splitext(path)
    mask = np.zeros(array.shape[:2], dtype=np.uint8)

    # take the time pixel by pixel and check if the average of the positive and negatives values is near to fifty
    threads = []
    for i in range(height):
        for j in range(width):
            threads.append(threading.Thread(target=checkPixel, args=(i, j, array[i, j, :], array.shape[2])))
            threads[-1].start()

    # Wait for all threads to finish
    while threading.active_count() > 1:
        pass

    # Save the mask
    saving = True
    saveSingleBand(name + "_mask" + ext, raster, mask, gdal.GDT_Byte, 'GTiff')
    saving = False
    start = False


   


def changeDetectorFile(path:str):
    """Calculate the change detector of raster image 

    Args:
        path (str): Path to the raster image
    """
    
    # Read raster
    rt, img, err, msg = loadRasterImage(path)
    if err:
        print(msg)
        sys.exit(1)

    changeDetector(img, path, rt)