from osgeo import gdal
import numpy as np
import os, sys
from tqdm import tqdm
    
def split(raster, bandcut):
   
    bands = raster.RasterCount
    outpath = os.path.dirname(raster.GetDescription())
    filename = raster.GetDescription().split("/")[-1].split(".")[0]
    
    # create the first part
    driver = raster.GetDriver()
    name = filename + f"_1-{bandcut}.tif"
    outfile = driver.Create(name, raster.RasterXSize, raster.RasterYSize, bandcut, gdal.GDT_Int16)
    cont = 0
    for i in tqdm(range(1,bands+1)):
        cont += 1
        if i == bandcut:
            band = raster.GetRasterBand(i)
            outfile.GetRasterBand(cont).WriteArray(band.ReadAsArray())
            outfile.SetGeoTransform(raster.GetGeoTransform())
            outfile.SetProjection(raster.GetProjection())
            outfile.FlushCache()
            # create the second part
            dif = bands - bandcut
            name = filename + f"_{bandcut+1}-{bands}.tif"
            outfile = driver.Create(name, raster.RasterXSize, raster.RasterYSize, dif, gdal.GDT_Int16)
            cont = 0
        else:
            band = raster.GetRasterBand(i)
            outfile.GetRasterBand(cont).WriteArray(band.ReadAsArray())
    outfile.SetGeoTransform(raster.GetGeoTransform())
    outfile.SetProjection(raster.GetProjection())
    outfile.FlushCache()


def splitfile(path, bandcut):
    """Split a raster file into two files

    Args:
        path (str): path to the raster file
        bandcut (int): band to split the file
    """
    raster = gdal.Open(path)
    if not raster:
        print("Error: could not open image")
        sys.exit(1)
    split(raster, bandcut)

def main():
    if len(sys.argv) != 3:
        print("Usage: python split.py <path/to/image.tif> <bandcut>")
        sys.exit(1)
    global path    
    path = sys.argv[1]
    try:
        bandcut = int(sys.argv[2])
    except ValueError:
        print("Usage: python split.py <path/to/image.tif> <bandcut>")
        print("Error: band must be an integer")
        sys.exit(1)
        
    raster = gdal.Open(path)
    if not raster:
        print("Error: could not open image")
        sys.exit(1)
    split(raster, bandcut)
    
    

if __name__ == '__main__':
    main()