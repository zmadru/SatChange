## Author Diego Madruga Ramos
## Version 5.0
"""
Author: Diego Madruga Ramos
Version: 5.0

This script creates a stack with the input directory files between the given dates, the files must be in the format: [tilename]_[year][month][day]*.tif
Has two modes:
    - Interactive mode: The user is asked the input and output directories
    - Import mode: The user can import the file and call the stack function
"""
## Neccesary imports for the correct work of the code
import gc
import time
import platform
import os
import sys
import pathlib
from osgeo import gdal
import numpy as np
import csv
import pandas as pd
from tqdm import tqdm

## Globals variables----------------------------------------------
outdata = None  # output data
total: int = 0
progress: int = 0
start: bool = False
out_file = None
saving: bool = False
# Detect the OS to set the correct comand to clean the screen
if platform.system() == "Windows":
    clear = "cls"
else:
    clear = "clear"

## Functions-----------------------------------------------------
# Method which ask the user the neccesary directories
def __askDirs():
    """
    Ask the user the neccesary directories
    
    Returns:
        tuple(str, str): The input and output directories
    """
    # global dir_in, dir_out

    run = True
    error = False
    #Asking the input directory, and check if exists
    while run:
        os.system(clear)
        if error:
            print("The directory doesnt exit")

        print("Write the input directory: ")
        dir_in = input()
        print("Its is correct the directory? (yes/no) \n->", dir_in)
        res = input().lower()
        if res == "yes" and os.path.exists(dir_in):
            run = False
        elif not os.path.exists(dir_in): # Check if the input exists
            error = True
    
    run = True
    #Asking the output directory, if doesnt exist is going to be created
    while run:
        os.system(clear)
        print("Write the output directory: ")
        dir_out = input()
        print("Its is correct the directory? (yes/no) \n->", dir_out)
        res = input().lower()
        if res == "yes":
            run = False
       
    # Print the both directories 
    os.system(clear)
    print("Input directory \t-> ",dir_in,"\nOutput directory \t-> ",dir_out)
    return dir_in, dir_out



# Method which takes all the files from a year and make a year stack
def __readDir(in_files: list) -> None:
    """
    Takes all the files from min_year to max_year and make a stack

    Args:
        min_year (int): The lower year in the directory
        max_year (int): The higher year in the directory
        in_files (list): The input files
    """
    global outdata, progress, start
    progress = 0
    start = True

    for file in tqdm(in_files):
        src_file = gdal.Open(file)  # Open de file from de dir_in
        band = np.array(src_file.GetRasterBand(1).ReadAsArray().astype('float32'))  # Save the file as a band
        band = 10000 * np.nan_to_num(band)   # Multiply by 10000 to get the integer value
        outdata.GetRasterBand(progress+1).WriteArray(band)    # Join the band to the stack 
        del band, src_file   # Free the variables
        gc.collect()    # Clean the memory
        progress += 1


        
def stack(in_files: list, dir_out: str, out_name: str):
    """
    # Stack
    Creates a stack with the input files, and saves the stack with the [out_name] on the [dir_out]

    ## Args:
        in_files (list): Input files
        dir_out (str): Output directory
        out_name (str): Output filename

    ## Returns:
        str: The output file path
    """
    global outdata, total, out_file, saving
    total = 0

    # Get the first file to get the metadata
    in_files = sorted(in_files)   # Take the year files sorted 
    src_file = gdal.Open(in_files[0])  # Open de file from de dir_in
    band = np.array(src_file.GetRasterBand(1).ReadAsArray().astype('float32'))  # Save the file as a band

    # Get the metadata
    cols = src_file.RasterXSize
    rows = src_file.RasterYSize
    bands = len(in_files)
    

    total = bands

    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(dir_out+"/temp.tif", cols, rows, bands, gdal.GDT_Int16)  # Create the stack file
    del band        # Free the variables
    gc.collect()    # Clean the memory
    
    __readDir(in_files) # Call the readDir function

    # Save the stack
    saving = True
    outdata.SetGeoTransform(src_file.GetGeoTransform())  # Set the geotransform
    outdata.SetProjection(src_file.GetProjection())  # Set the projection
    outdata.FlushCache()  # Flush the cache
    del outdata, src_file# Free the variables
    gc.collect()    # Clean the memory
    gdal.Translate(dir_out+"/"+out_name+".tif", dir_out+"/temp.tif", format="GTiff", creationOptions=["INTERLEAVE=BAND"]) # Convert the stack to BSQ format
    os.remove(dir_out+"/temp.tif") # Remove the stack in BIL format
    out_file = dir_out+"/"+out_name+".tif" # Return the stack path
    saving = False



## Main--------------------------------------------------------------
def main():
    if len(sys.argv) != 4:
        print("\nUsage: ",sys.argv[0],"<stack name> <files directory> <output directory>")
        sys.exit(1)

    stack_name = sys.argv[1]
    indir = sys.argv[2]
    outdir = sys.argv[3]    
    
    # get the files from the directory
    files = [f for f in os.listdir(indir) if os.path.isfile(os.path.join(indir, f))]
    stack(files, outdir, stack_name)



if __name__ == "__main__":
    main()