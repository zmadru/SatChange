import os, sys
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
#import gdal, osr
import numpy as np
from tqdm.contrib import itertools
from lib.load_save_raster import loadRasterImage, saveSingleBand


# Global variables
progress:int = 0
out_file = None
saving:bool = False
start:bool = False
out_array:np.ndarray = None
rt = None

def saveShapefile(dst):
    """Save the mask as shapefile

    Args:
        dst (str): name of the output
    """
    raster = gdal.Open(dst+'.tif')
    geotransform = raster.GetGeoTransform()
    array = mask
    
    # Convert array to points
    count = 0
    roadList = np.where(array == 1)
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    for indexY in roadList[0]:
        indexX = roadList[1][count]
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        Xcoord = originX+pixelWidth*indexX
        Ycoord = originY+pixelHeight*indexY
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(Xcoord, Ycoord)
        multipoint.AddGeometry(point)
        count += 1
    
    # Save point coordinates to Shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    outshp = driver.CreateDataSource(dst+'.shp')
    outLayer = outshp.CreateLayer(dst+'.shp', geom_type=ogr.wkbMultiPoint)
    featureDefn = outLayer.GetLayerDefn()
    outFeature = ogr.Feature(featureDefn)
    outFeature.SetGeometry(multipoint)
    outLayer.CreateFeature(outFeature)
    outFeature = None
    
    
    
def checkPixel(i, j, array, numfilesyear:int):
    """Check the time serie analizing the maximun and minimun functions

    Args:
        i (int): Row
        j (int): Column
        array (np.array): Time serie of the pixel
        numfilesyear (int): Number of files per year
    """
    global mask, progress
    
    n = len(array) // numfilesyear
    halfyear = numfilesyear // 2
    
    minini = array[halfyear-1]
    
    minlast = array[(halfyear-1)+numfilesyear*(n-1)]
    if (minini - minlast) >= 10:
        mask[i, j] = 1
        
    progress += 1
    
def checkPixel2(i, j, array):
    """Analize the upper and lower limits of the time serie

    Args:
        i (_type_): _description_
        j (_type_): _description_
        array (_type_): _description_
    """
    global mask, progress
    
    std = np.std(array)
    upperlimit = np.mean(array) + 2*std
    lowerlimit = np.mean(array) - 2*std
    
    if np.where(array > upperlimit)[0].size < 0 or np.where(array < lowerlimit)[0].size < 0:
        mask[i, j] = 1
    
    progress += 1
        


def changeDetector(array:np.ndarray, path:str, raster):
    """Calculate the change detector of an array given an array
    
    Args:
        array (np.ndarray): Matrix of the raster image autocorrelation
        path (str): Path to the raster image
        raster (Dataset GDAL object): Object that contains the structure of the raster file
        numfilesyear (int): Number of files per year
    """
    global progress, out_file, saving, out_array, start, mask, total, mask2

    progress = 0
    saving = False
    start = True
    total = array.shape[0]*array.shape[1]
    # send the total to the progress bar
    # Read raster
    height, width = array.shape[:2]
    name, ext = os.path.splitext(path)
    # mask = np.zeros(array.shape[:2], dtype=np.uint8)
    
    # # take the time pixel by pixel and check if the average of the positive and negatives values is near to fifty
    # for i, j in itertools.product(range(height), range(width)):
    #     checkPixel(i, j, array[i, j], numfilesyear)
    n = array.shape[2] // 2
    fhalf = array[:, :, :n]
    shalf = array[:, :, n:]

    fhalf = np.sum(fhalf, axis=2)
    shalf = np.sum(shalf, axis=2)

    result = fhalf - shalf
    result = result/10000
    mask = np.where(result >= 0.165, 1, result)
    mask = np.where(mask < 0.165, 0, mask)

    progress = 100
    # Save the mask
    saving = True
    out_file = name + "_mask"
    # saveSingleBand(out_file+str(sensivity), raster, mask, gdal.GDT_Byte, 'GTiff')
    saveSingleBand(out_file, raster, mask, gdal.GDT_Byte, 'GTiff')
    
    saving = False
    start = False


def changeDetectorFile(path:str, numfilesyear):
    """Calculate the change detector of raster image 

    Args:
        path (str): Path to the raster image
    """
    # Read raster
    print("Loading raster image..." + path)
    rt, img, err, msg = loadRasterImage(path) 
    if err:
        print(msg)
        sys.exit(1)

    changeDetector(img, path, rt)
    
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 change_detector.py <file>")
        print("<file>: path to the raster image")
        sys.exit(1)
        
    changeDetectorFile(sys.argv[1], 2)