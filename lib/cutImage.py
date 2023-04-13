from osgeo import gdal
import sys

def cut(raster, shapefile, output):
    """Cuts a raster file with a shapefile.

    Args:
        raster (str): path to the raster file
        shapefile (str): path to the shapefile
        output (str): path to the output file
    """
    gdal.Warp(output, raster, cutlineDSName=shapefile, cropToCutline=True)

def cutfiles(raster, shapefile, output):
    """Cuts a raster file with a shapefile.

    Args:
        raster (str): path to the raster file
        shapefile (str): path to the shapefile
        output (str): path to the output file
    """
    gdal.Warp(output, raster, cutlineDSName=shapefile, cropToCutline=True)

def main():
    if len(sys.argv) < 4:
        print("Usage: python cutImage.py [options] <rasterfile> <shapefilesDir> <ncuts>")
        print("Options: -f <output> <rasterfile> <shapefile>\n-d  <rasterfile> <shapefilesDir> <ncuts>")
        sys.exit(1)
    elif len(sys.argv) == 5:
        if sys.argv[1] == "-f":
            output = sys.argv[2]
            raster = sys.argv[3]
            shapefile = sys.argv[4]
            cut(raster, shapefile, output)
            sys.exit(0)
       
        
    raster = gdal.Open(sys.argv[1])
    name, ext = sys.argv[1].split('.')
    shapefilesDir = sys.argv[2]
    shape = shapefilesDir.split('/')[-1]
    ncuts = int(sys.argv[3])
    # cut the raster with the shapefile
    for i in range(1, ncuts+1):
        gdal.Warp(f'{name}_C{i}.tif', raster, cutlineDSName=f"{shapefilesDir}/{shape}_C{i}/{shape}_C{i}.shp", cropToCutline=True)
    

if __name__ == '__main__':
    main()