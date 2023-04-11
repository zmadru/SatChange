import os, sys
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
#import gdal, osr
import numpy as np
from tqdm.contrib import itertools


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
    output = geotiff.Create(dst+'.tif', rt.RasterXSize, rt.RasterYSize, 1,tt)
    wkt = rt.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    output.GetRasterBand(1).WriteArray(img)
    output.GetRasterBand(1).SetNoDataValue(-999)
    output.SetGeoTransform(transform)
    output.SetProjection(srs.ExportToWkt())
    output = None
    # Save as a shpefile
    saveShapefile(dst)
    proj = rt.GetProjection()
    prj = open(dst+'.prj', 'w')
    prj.write(proj)
    prj.close()


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
        


def changeDetector(array:np.ndarray, path:str, raster, numfilesyear:int):
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
    mask = np.zeros(array.shape[:2], dtype=np.uint8)
    
    # take the time pixel by pixel and check if the average of the positive and negatives values is near to fifty
    for i, j in itertools.product(range(height), range(width)):
        checkPixel(i, j, array[i, j], numfilesyear)

    progress = height*width
    # Save the mask
    saving = True
    out_file = name + "_mask"
    # saveSingleBand(out_file+str(sensivity), raster, mask, gdal.GDT_Byte, 'GTiff')
    saveSingleBand(out_file, raster, mask, gdal.GDT_Byte, 'GTiff')
    
    saving = False
    start = False


def changeDetectorFile(path:str, cicle:int):
    """Calculate the change detector of raster image 

    Args:

        path (str): Path to the raster image
        cicly (int): Number of files per year
    """
    # Read raster
    rt, img, err, msg = loadRasterImage(path) 
    if err:
        print(msg)
        sys.exit(1)

    changeDetector(img, path, rt, cicle)
    
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 change_detector.py <file> <numfilesyear>")
        print("<file>: path to the raster image, <numfilesyear>: number of files per year")
        sys.exit(1)
        
    changeDetectorFile(sys.argv[1], int(sys.argv[2]))