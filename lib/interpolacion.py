import os, sys
#import gdal, osr
import numpy as np
from scipy import interpolate
from osgeo import gdal
from osgeo import osr
from tqdm import tqdm
from lib.load_save_raster import loadRasterImage, saveBand
from concurrent.futures import ProcessPoolExecutor
import gc
import warnings


# Global variables
progress:int = 0
out_file = None
saving:bool = False
array:np.ndarray = None
rt = None


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
        A = np.where(A != value, A, f(inds)).astype(np.int16)           
    return A

def process_row_interp(args):
    i, row, modeInterp = args
    for j in range(row.shape[0]):
        row[j, :] = fill(row[j, :], 0, modeInterp)
    return i, row

# Main
def getFiltRaster(path:str, modeInterp:str='linear'):
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
    # aux = np.zeros(img.shape).astype(np.int16)

    # Dims
    height, width, depth = img.shape
    print(img.shape)
    # Dims
    height, width, depth = img.shape
    print(img.shape)

    rows = [(i, img[i, :, :], modeInterp) for i in range(height)]

    with ProcessPoolExecutor(max_workers=os.cpu_count()//2) as executor:
        for i, row_interp in tqdm(executor.map(process_row_interp, rows), total=height, desc="Interpolating"):
            img[i, :, :] = row_interp
            progress = int((i + 1) / height * 100)
    
    progress = 100
    # Save
    dst = f'{name}_filt_{modeInterp}_{ext}'
    out_file = dst
    array = img
    print("Saving in ", dst)
    saveBand(dst, rt, img, tt=gdal.GDT_Int16)
        

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 interpolacion.py <path> <saveformat>\n<path>: Path to raster image\n <saveformat>: Format to save the raster image(int16, float32)")
        sys.exit(1)
        
    path = sys.argv[1]
    # saveformat = sys.argv[2]
    print("Path: ", path)
    getFiltRaster(path, modeInterp='linear')
    
###en el método de llenado borra todo y deja el que diga 'linear' , es el que mejor se comporta. , 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'