"""
Calculates the indexes of the given images and sensor.
    AUTHOR:  Diego Madruga Ramos
    version: 0.1
"""
import gc
import numpy as np
from osgeo import gdal

#  Global variables
progress = 0
start = False

def calculateIndex(index:str, files:list, out_dir:str, sensor:str):
    """
    Calculates the index of the given images depending on the sensor.
    
    Args:
        index (str): The index to calculate
        files (list): The list of files to calculate the index
        out_dir (str): The output directory
        sensor (str): The sensor of the images
    """

    if index == "NDVI":
        ndvi(files, out_dir, sensor)
    else:
        print("The index is not implemented")


def ndvi(files:list, out_dir:str, sensor:str):
    """
    Calculates the NDVI of the given images depending on the sensor.
    
    Args:
        files (list): The list of files to calculate the index
        out_dir (str): The output directory
        sensor (str): The sensor of the images
    """
    global progress, start
    progress = 0
    start = True

    for file in files:
        src_file = gdal.Open(file)  # Open de file from de dir_in
        # get bands from the file depending on the sensor
        if sensor == "Sentinel 2 (10m)": # bands 4 and 8
            band_red = np.array(src_file.GetRasterBand(3).ReadAsArray().astype('float32')) 
            band_nir = np.array(src_file.GetRasterBand(4).ReadAsArray().astype('float32'))  
        elif sensor == "Sentinel 2 (20m)": # bands 4 and 8a
            band_red = np.array(src_file.GetRasterBand(3).ReadAsArray().astype('float32'))  
            band_nir = np.array(src_file.GetRasterBand(7).ReadAsArray().astype('float32')) 
        elif sensor == "Sentinel 2 (60m)": # bands 4 and 8b
            band_red = np.array(src_file.GetRasterBand(4).ReadAsArray().astype('float32'))
            band_nir = np.array(src_file.GetRasterBand(8).ReadAsArray().astype('float32'))
        elif sensor in ["Modis", "AVHRR"]: # bands 1 and 2
            band_red = np.array(src_file.GetRasterBand(1).ReadAsArray().astype('float32'))
            band_nir = np.array(src_file.GetRasterBand(2).ReadAsArray().astype('float32'))

        # Calculate the NDVI
        ndvi = np.array((band_nir - band_red) / (band_nir + band_red))
        del band_red, band_nir, src_file   # Free the variables
        gc.collect()    # Clean the memory

        # Save the NDVI
        name = file.split("/")[-1].split(".")[0]  # Get the name of the file
        print("Calculating the index of the file: ", name)
        driver = gdal.GetDriverByName("GTiff")
        # Create the output file
        ndviFile = driver.Create(f"{out_dir}/{name}_NDVI.tif", src_file.RasterXSize, src_file.RasterYSize, 1, gdal.GDT_Float32)
        ndviFile.GetRasterBand(1).WriteArray(ndvi)  # Write the array to the file
        ndviFile.SetGeoTransform(src_file.GetGeoTransform())  # Set the GeoTransform
        ndviFile.SetProjection(src_file.GetProjection())  # Set the Projection
        ndviFile.FlushCache()  # Flush the cache
        del ndviFile, ndvi  # Free the variables
        gc.collect()    # Clean the memory
        progress += 1   # Increase the progress

        
    
