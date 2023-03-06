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
indexes = ["NDVI", "NBR"]
sensors = ["Modis", "AVHRR"]
# sensors = ["Sentinel 2 (10m)", "Sentinel 2 (20m)", "Sentinel 2 (60m)", "Modis", "AVHRR"]
processed = []

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
    elif index == "NBR":
        if nbr(files, out_dir, sensor) == -1:
            print("Cant calculate NBR for the selected sensor")
    else:
        print("The index is not implemented")


def ndvi(files:list, out_dir:str, sensor:str) -> int:
    """
    Calculates the NDVI of the given images depending on the sensor.
    
    Args:
        files (list): The list of files to calculate the index
        out_dir (str): The output directory
        sensor (str): The sensor of the images
    Returns:
        error (int): 0 okay, -1 error
    """
    global progress, start, processed
    processed = []
    progress = 0
    start = True

    for file in files:
        src_file = gdal.Open(file, gdal.GA_ReadOnly)  # Open de file from de dir_in
        ext = file.split(".")[-1]  # Get the extension of the file
        
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
        elif ext == "hdf":
            aux = src_file.GetSubDatasets()
            band_red = gdal.Open(aux[0][0]).ReadAsArray()
            band_nir = gdal.Open(aux[1][0]).ReadAsArray()
        elif sensor in ["Modis", "AVHRR"]: # bands 1 and 2
            band_red = np.array(src_file.GetRasterBand(1).ReadAsArray().astype('float32'))
            band_nir = np.array(src_file.GetRasterBand(2).ReadAsArray().astype('float32'))

        # Calculate the NDVI
        op1 = band_nir - band_red
        op2 = band_nir + band_red
        op2 = np.where(op2 == 0, np.nan, op2)
        ndvi = np.array( op1 / op2)
        # del band_red, band_nir, src_file   # Free the variables
        gc.collect()    # Clean the memory

        # Save the NDVI
        name = file.split("/")[-1].split(".")[:-1]  # Get the name of the file
        name = "_".join(name)   # Join the name
        print("Calculating the index of the file: ", name)
        driver = gdal.GetDriverByName("GTiff")
        # Create the output file
        ndviFile = driver.Create(f"{out_dir}/{name}_NDVI.tif", band_nir.shape[1], band_nir.shape[0], 1, gdal.GDT_Float32)
        processed.append(f"{out_dir}/{name}_NDVI.tif")
        ndviFile.GetRasterBand(1).WriteArray(ndvi)  # Write the array to the file
        ndviFile.SetGeoTransform(src_file.GetGeoTransform())  # Set the GeoTransform
        ndviFile.SetProjection(src_file.GetProjection())  # Set the Projection
        ndviFile.FlushCache()  # Flush the cache
        del ndviFile, ndvi  # Free the variables
        gc.collect()    # Clean the memory
        progress = (progress + 1)/len(files) * 100
    progress = 100
    return 0


def nbr(files:list, out_dir:str, sensor:str) -> int:
    """
    Calculates the NBR of the given images depending on the sensor.
    
    Args:
        files (list): The list of files to calculate the index
        out_dir (str): The output directory
        sensor (str): The sensor of the images
    Returns:
        error (int): 0 okay, -1 error
    """
    global progress, start, processed
    processed = []
    progress = 0
    start = True

    for file in files:
        src_file = gdal.Open(file)  # Open de file from de dir_in
        # get bands from the file depending on the sensor
        if sensor == "Sentinel 2 (10m)": # bands 2 and 8
            return -1
        if sensor == "Sentinel 2 (20m)": # bands 12 and 8a
            band_red = np.array(src_file.GetRasterBand(11).ReadAsArray().astype('float32'))  
            band_nir = np.array(src_file.GetRasterBand(7).ReadAsArray().astype('float32')) 
        elif sensor == "Sentinel 2 (60m)": # bands 4 and 8b
            band_red = np.array(src_file.GetRasterBand(4).ReadAsArray().astype('float32'))
            band_nir = np.array(src_file.GetRasterBand(8).ReadAsArray().astype('float32'))
        elif sensor in ["Modis", "AVHRR"]: # bands 1 and 2
            band_red = np.array(src_file.GetRasterBand(1).ReadAsArray().astype('float32'))
            band_nir = np.array(src_file.GetRasterBand(2).ReadAsArray().astype('float32'))

        # Calculate the NBR
        nbr = np.array((band_nir - band_red) / (band_nir + band_red))
        del band_red, band_nir, src_file   # Free the variables
        gc.collect()    # Clean the memory

        # Save the NBR
        name = file.split("/")[-1].split(".")[0]  # Get the name of the file
        print("Calculating the index of the file: ", name)
        driver = gdal.GetDriverByName("GTiff")
        # Create the output file
        nbrFile = driver.Create(f"{out_dir}/{name}_NBR.tif", src_file.RasterXSize, src_file.RasterYSize, 1, gdal.GDT_Float32)
        # add the name to the list of processed files
        processed.append(f"{out_dir}/{name}_NBR.tif")
        nbrFile.GetRasterBand(1).WriteArray(nbr)  # Write the array to the file
        nbrFile.SetGeoTransform(src_file.GetGeoTransform())  # Set the GeoTransform
        nbrFile.SetProjection(src_file.GetProjection())  # Set the Projection
        nbrFile.FlushCache()  # Flush the cache
        del nbrFile, nbr  # Free the variables
        gc.collect()    # Clean the memory
        progress += 1   # Increase the progress
        return 0

        
    
