from osgeo import gdal
import numpy as np
import sys, os
from tqdm.contrib import itertools

def zeros(array, ini, fin):
    """Calculate the number of zeros in an array

    Args:
        array (np.ndarray): Array of zeros and ones
        ini (int): Initial value
        fin (int): Final value
    Returns:
        int: Number of zeros
    """
    count = np.zeros(16)
    flag = 0
    gap = 0
    if fin > len(array):
        fin = len(array)
    for i in range(ini-1,fin):
        n = array[i] 
        if n == 0:
            flag += 1
        else:
            if flag > 0:
                if flag > gap:
                    gap = flag
                if flag > 16:
                    flag = 16
                count[flag-1] += 1 
                flag = 0
        if flag > 0 and i == fin-1:
            if flag > gap:
                gap = flag
            if flag > 16:
                flag = 16
            count[flag-1] += 1
        
    res = np.append(gap, count)
    return res

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 zerosViability.py <file> <initial value> <final value>")
        sys.exit(1)
        
    path = sys.argv[1]
    ini = int(sys.argv[2])
    fin = int(sys.argv[3])
    
    if ini > fin:
        print("Initial value must be less than final value")
        sys.exit(1)
        
    raster = gdal.Open(path)
    if raster is None:
        print("Error opening raster")
        sys.exit(1)
        
    # Read raster
    img = np.stack([raster.GetRasterBand(i).ReadAsArray() for i in range(1, raster.RasterCount + 1)], axis=2)
    print(img.shape)
    mask = np.zeros((img.shape[0], img.shape[1], 17))
    
    for i, j in itertools.product(range(img.shape[0]), range(img.shape[1])):
        mask[i,j,:] = zeros(img[i,j,:], ini, fin)
        
        
    # Save raster
    driver = raster.GetDriver()
    name, ext = os.path.splitext(path)
    filename = f'{name}_mask{ext}'
    output = driver.Create(filename, raster.RasterXSize, raster.RasterYSize, 17, gdal.GDT_Int16)
    output.SetGeoTransform(raster.GetGeoTransform())
    output.SetProjection(raster.GetProjection())
    for i in range(1, 17+1):
        output.GetRasterBand(i).WriteArray(mask[:,:,i-1])
        if i == 1:
            output.GetRasterBand(i).SetDescription('Longest gap')
        else:
            output.GetRasterBand(i).SetDescription(f'Gap of {i-1} zeros')
    
    output.FlushCache()
