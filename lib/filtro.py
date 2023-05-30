import filtro_SGV1 as SGV1
import filtro_MAX as MAX
import filtro_FFT as FFT
import filtro_Whit as Whit
import numpy as np

# global variables
filtro:str = ""
out_file:str = ""
out_array:np.ndarray = None
rt = None

def getFiltRaster(path:str, option:str):
    """
    Get raster filtered
    
    Args:
        path (str): Path to raster
        option (str): Filter to apply: SGV, MAX, FFT, WHIT
    """
    global filtro, out_file, out_array, rt
    
    filtro = option
    if filtro == "SGV":
        SGV1.getFiltRaster(path, 3, 2)
        out_file = SGV1.out_file
        out_array = SGV1.out_array
        rt = SGV1.rt
    elif filtro == "MAX":
        MAX.getFiltRaster(path)
        out_file = MAX.out_file
        out_array = MAX.out_array
        rt = MAX.rt
    elif filtro == "FFT":
        FFT.getFiltRaster(path)
        out_file = FFT.out_file
        out_array = FFT.out_array
        rt = FFT.rt
    elif filtro == "WHIT":
        Whit.getFiltRaster(path)
        out_file = Whit.out_file
        out_array = Whit.out_array
        rt = Whit.rt
        
def getFilter(array:np.ndarray, option:str, path:str, raster):
    """
    Get array filtered
    
    Args:
        array (np.ndarray): Array to be filtered
        option (str): Filter to apply: SGV, MAX, FFT, WHIT
        path (str): Path to output file
        raster (gdalDataSet): Raster object
    """
    global filtro, out_file, out_array, rt
    filtro = option
    
    if filtro == "SGV":
        SGV1.getFilter(array, 3, 2, path, raster)
        out_file = SGV1.out_file
        out_array = SGV1.out_array
        rt = SGV1.rt
    elif filtro == "MAX":
        MAX.getFilter(array, path, raster)
        out_file = MAX.out_file
        out_array = MAX.out_array
        rt = MAX.rt
    elif filtro == "FFT":
        FFT.getFilter(array, path, raster)
        out_file = FFT.out_file
        out_array = FFT.out_array
        rt = FFT.rt
    elif filtro == "WHIT":
        Whit.getFilter(array, path, raster)
        out_file = Whit.out_file
        out_array = Whit.out_array
        rt = Whit.rt
        
def getProgress():
    if filtro == "SGV":
        return SGV1.progress
    elif filtro == "MAX":
        return MAX.progress
    elif filtro == "FFT":
        return FFT.progress
    elif filtro == "WHIT":
        return Whit.progress
    
def getOutFile():
    if filtro == "SGV":
        return SGV1.out_file
    elif filtro == "MAX":
        return MAX.out_file
    elif filtro == "FFT":
        return FFT.out_file
    elif filtro == "WHIT":
        return Whit.out_file
    
def getOutArray():
    if filtro == "SGV":
        return SGV1.out_array
    elif filtro == "MAX":
        return MAX.out_array
    elif filtro == "FFT":
        return FFT.out_array
    elif filtro == "WHIT":
        return Whit.out_array
    
def getRt():
    if filtro == "SGV":
        return SGV1.rt
    elif filtro == "MAX":
        return MAX.rt
    elif filtro == "FFT":
        return FFT.rt
    elif filtro == "WHIT":
        return Whit.rt

def getSaving():
    if filtro == "SGV":
        return SGV1.saving
    elif filtro == "MAX":
        return MAX.saving
    elif filtro == "FFT":
        return FFT.saving
    elif filtro == "WHIT":
        return Whit.saving
    
def getStart():
    if filtro == "SGV":
        return SGV1.start
    elif filtro == "MAX":
        return MAX.start
    elif filtro == "FFT":
        return FFT.start
    elif filtro == "WHIT":
        return Whit.start

