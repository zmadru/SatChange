from osgeo import gdal
import numpy as np
import sys, os
from tqdm.contrib import itertools
import tqdm

#  variables globales
pesos = {
    1:0.5,
    2:0.5,
    3:0.5,
    4:0.6,
    5:0.6,
    6:0.6,
    7:2,
    8:2,
    9:2,
    10:5,
    11:5,
    12:5,
    13:10,
    14:10,
    15:10,
    16:20,
}
start = False
progress:int = 0
saving = False
output:str = ''

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
    mayores16 = []
    if fin > len(array):
        fin = len(array)
        
    length = fin - ini + 1
    for i in range(ini-1,fin):
        n = array[i] 
        if n == 0:
            flag += 1
        else:
            if flag > 0:
                if flag > gap:
                    gap = flag
                if flag > 16:
                    mayores16.append(flag)
                    flag = 16
                count[flag-1] += 1 
                flag = 0
        if flag > 0 and i == fin-1:
            if flag > gap:
                gap = flag
            if flag > 16:
                mayores16.append(flag)
                flag = 16
            count[flag-1] += 1
    viability = 0
    i = 1
    for n in count:
        if i < 16:
            viability += n * pesos[i]    
        else:      
            if len(mayores16) > 0:
                aux = n - len(mayores16)
                viability += aux * pesos[16]
                for m in mayores16:
                    viability += pesos[16] + (m*100)/length
            else:
                viability += n * pesos[16]
        i += 1  
    
    viability = viability*100 / length
    viability:int = 100 - viability
    res = np.append(viability, gap)
    res = np.append(res, count)
    return res

def main(path , ini, fin):
    global start, progress, saving, output
    raster = gdal.Open(path)
    if raster is None:
        print("Error opening raster")
        sys.exit(1)
        
    # Read raster
    img = np.stack([raster.GetRasterBand(i).ReadAsArray() for i in tqdm.tqdm(range(1, raster.RasterCount + 1), desc='Loading Image')], axis=2)
    print(img.shape)
    mask = np.zeros((img.shape[0], img.shape[1], 18))
    start = True
    for i, j in itertools.product(range(img.shape[0]), range(img.shape[1]), desc='Calculating zeros'):
        mask[i,j,:] = zeros(img[i,j,:], ini, fin)
        progress = (i*img.shape[1] + j) / (img.shape[0]*img.shape[1]) * 100   
    progress = 100
    # Save raster
    saving = True
    driver = raster.GetDriver()
    name, ext = os.path.splitext(path)
    filename = f'{name}_mask{ext}'
    output = driver.Create(filename, raster.RasterXSize, raster.RasterYSize, 18, gdal.GDT_Int16)
    output.SetGeoTransform(raster.GetGeoTransform())
    output.SetProjection(raster.GetProjection())
    for i in range(1, 18+1):
        output.GetRasterBand(i).WriteArray(mask[:,:,i-1])
        if i == 1:
            output.GetRasterBand(i).SetDescription('Viability')
        elif i == 2:
            output.GetRasterBand(i).SetDescription('Longest gap')
        else:
            output.GetRasterBand(i).SetDescription(f'Gap {i-2} zeros')
    
    output.FlushCache()
    output = filename
    start = False
    saving = False
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
    
    main(path, ini, fin)
    
