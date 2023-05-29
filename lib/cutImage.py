from osgeo import gdal
import sys, os
from tqdm import tqdm

def cut(raster, shapefile, output):
    """Cuts a raster file with a shapefile.

    Args:
        raster (str): path to the raster file
        shapefile (str): path to the shapefile
        output (str): path to the output file
    """
    gdal.Warp(output, raster, cutlineDSName=shapefile, cropToCutline=True)

def cutfiles(raster, shapefilesdir, output):
    """Cuts a raster file with a shapefile.

    Args:
        raster (str): path to the raster file
        shapefilesdir (str): path to the shapefiles directory
        output (str): path to the output file
    """
    outputdir = os.path.join(output, "Cuts")
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    # get the .shp files in the directory
    shapefiles = [os.path.join(shapefilesdir, f) for f in os.listdir(shapefilesdir) if f.endswith('.shp')]
    for shapefile in tqdm(shapefiles):
        tqdm.write(f"Cutting {shapefile}...")
        name = os.path.basename(shapefile).split('.')[0]
        
        outputdirCCAA = os.path.join(outputdir, name)
        if not os.path.exists(outputdirCCAA):
            os.makedirs(outputdirCCAA)
            
        name = os.path.join(outputdirCCAA, name+'.tif')
        gdal.Warp(name, raster, cutlineDSName=shapefile, cropToCutline=True)

def main():
    if len(sys.argv) < 4:
        print("Usage: python cutImage.py [options] <rasterfile> <shapefilesDir> <ncuts>")
        print("Options: -f <output> <rasterfile> <shapefile>\n-d  <rasterfile> <shapefilesDir> <output>")
        sys.exit(1)
    elif len(sys.argv) == 5:
        if sys.argv[1] == "-f":
            output = sys.argv[2]
            raster = sys.argv[3]
            shapefile = sys.argv[4]
            cut(raster, shapefile, output)
            sys.exit(0)
        elif sys.argv[1] == "-d":
            raster = sys.argv[2]
            shapefilesDir = sys.argv[3]
            output = sys.argv[4]
            cutfiles(raster, shapefilesDir, output)
            sys.exit(0)
       
        
    # raster = gdal.Open(sys.argv[1])
    # name, ext = sys.argv[1].split('.')
    # shapefilesDir = sys.argv[2]
    # shape = shapefilesDir.split('/')[-1]
    # ncuts = int(sys.argv[3])
    # # cut the raster with the shapefile
    # for i in range(1, ncuts+1):
    #     gdal.Warp(f'{name}_C{i}.tif', raster, cutlineDSName=f"{shapefilesDir}/{shape}_C{i}/{shape}_C{i}.shp", cropToCutline=True)
    

if __name__ == '__main__':
    main()