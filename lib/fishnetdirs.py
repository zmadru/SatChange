"""
# Fishnet.py
Create a fishnet shapefile from a raster file

## Author: Diego Madruga Ramos    
"""
from osgeo import ogr
from osgeo import gdal
import sys, os
from math import ceil
from tqdm import tqdm

def openRaster(rasterfile):
    """Opens a raster file.

    Args:
        rasterfile (str): path to the raster file

    Returns:
        Dataset: gdal raster
    """
    try:
        raster = gdal.Open(rasterfile)
    except:
        print("Could not open raster file")
        sys.exit(1)
    return raster

def createFishnet(raster, nrows, ncols, shpname, outputDir):
    """
    Creates a fishnet shapefile from a raster file, with nrows and ncols.

    Args:
        raster (Dataset): gdal raster file
        nrows (int): number of rows
        ncols (int): number of columns
        shpname (str): name of the output shapefile
    """
    geoTransform = raster.GetGeoTransform()
    proj = raster.GetProjection()
    
    # Get the raster's extent
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymin = ymax + geoTransform[5] * raster.RasterYSize
    
    gridWidth = ceil((xmax - xmin) / ncols)
    gridHeight = ceil((ymax - ymin) / nrows)
    
    # start grid cell envelope
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight
    
    # Create the shapefile
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    name, ext = os.path.splitext(shpname)
    try:
        os.mkdir(outputDir+'/'+name)
    except OSError:
        pass
    outdata = outDriver.CreateDataSource(outputDir+'/'+name+'/'+name)
    outLayer = outdata.CreateLayer(name, geom_type=ogr.wkbPolygon)
    layerDfn = outLayer.GetLayerDefn()
    
    # Create the fields
    countcols = 0
    cont = 0
    # bar = tqdm(total=ncols*nrows)
    while countcols < ncols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        countrows = 0

        while countrows < nrows:
            countrows += 1
            cont += 1
            
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            outFeature = ogr.Feature(layerDfn)
            outFeature.SetGeometry(poly)
            outLayer.CreateFeature(outFeature)
            outFeature = None
            
            # save the new geo as a new shapefile
            aux = outDriver.CreateDataSource(outputDir+'/'+name+'/'+name+'_C'+str(cont))
            auxLayer = aux.CreateLayer(name+'_C'+str(cont), geom_type=ogr.wkbPolygon)
            auxDfn = auxLayer.GetLayerDefn()
            auxFeature = ogr.Feature(auxDfn)
            auxFeature.SetGeometry(poly)
            auxLayer.CreateFeature(auxFeature)
            auxFeature = None
            # create the prj file
            prj = open(outputDir+'/'+name+'/'+name+'_C'+str(cont)+'/'+name+'_C'+str(cont)+'.prj', 'w')
            prj.write(proj)
            prj.close()
            # cut the raster with the shapefile
            # dst = f'{outputDir}/{name}/{rasterfile}_C{cont}.tif'
            # shape = outputDir+'/'+name+'/'+name+'_C'+str(cont)+'/'+name+'_C'+str(cont)+'.shp'
            # gdal.Warp(dst, raster, cutlineDSName=shape, cropToCutline=True)

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight
            # bar.update(1)

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth
        
    outdata = None
    prj = open(outputDir+'/'+name+'/'+name+'/'+name+'.prj', 'w')
    prj.write(proj)
    prj.close()    

def fishnetfile(rasterfile, nrows, ncols, shpname, outputDir):
    """Creates a fishnet shapefile from a raster file, with nrows and ncols.

    Args:
        rasterfile (str): path to the raster file
        nrows (int): number of rows
        ncols (int): number of columns
        shpname (str): name of the output shapefile
    """
    raster = openRaster(rasterfile)
    createFishnet(raster, nrows, ncols, shpname, outputDir)
    
if __name__ == '__main__':
    if(len(sys.argv) != 6):
        print("Usage: fishnet.py <inputfile> <nRows> <nColums> <ShapefileName> <outputDir>")
        sys.exit(1)

    rasterfile = sys.argv[1]
    try:
        nrows = int(sys.argv[2])
        ncols = int(sys.argv[3])
    except:
        print("nRows and nCols must be integers")
        print("Usage: fishnet.py <inputfile> <nRows> <nColums> <ShapefileName> <outputDir>")
        sys.exit(1)
    shpname = sys.argv[4]
    outputDir = sys.argv[5]
    
    # Open the raster file
    raster = openRaster(rasterfile)
    
    # Create the fishnet
    createFishnet(raster, nrows, ncols, shpname, outputDir)
    
    
    
    
    
      