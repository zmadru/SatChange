import geemap
import ee
import os
import sys
import numpy as np
from osgeo import gdal, ogr, osr
import glob
import time

# global variables
roi: ee.FeatureCollection
tile: str
orbit: int
n_images: int = 0
get_n_images: bool = False
progress: int = 0


def provincias(provincia_name:str):
    global roi
    provincias = r"\\Tierra\bd_sigpac\Tiles_S2\recintos_provinciales_inspire_peninbal_etrs89\recintos_provinciales_inspire_peninbal_etrs89.shp"
    campo_nombre = "NAMEUNIT"

    # Abrir el shapefile
    ds = ogr.Open(provincias)

    geometry = None
    if ds is not None:
        # Obtener la primera capa (en caso de que haya varias)
        layer = ds.GetLayerByIndex(0)

        # Iterar sobre las features
        for feature in layer:
            # Obtener el valor del campo NAMEINIT
            nombre = feature.GetField(campo_nombre)
            if str(nombre).lower() == provincia_name.lower():
                print('Provincia encontrada.')
                # Obtener la geometría correspondiente a NAMEINIT
                geometry = feature.GetGeometryRef().Clone()
                break
        
        if geometry is None:
            print("No se encontró la provincia.")
            sys.exit(0)
    else:
        print("No se pudo abrir el shapefile.")

    # save the geometry as a temporary file
    tmp_dir = os.path.join('.', 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_file = os.path.join(tmp_dir, 'geometry.shp')
    driver = ogr.GetDriverByName('ESRI Shapefile')
    driver.DeleteDataSource(tmp_file)
    ds = driver.CreateDataSource(tmp_file)
    layer = ds.CreateLayer('geometry', geom_type=ogr.wkbPolygon)
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetGeometry(geometry)
    layer.CreateFeature(feature)
    ds = None

    # Convertir la geometría a un objeto de Earth Engine
    roi = geemap.shp_to_ee(tmp_file)
    
def detect_tile(name:str):
    global roi, tile, orbit
    
    ee.Initialize()
    
    # check if the input is a shapefile or a province name
    if name.endswith('.shp'):
        roi = geemap.shp_to_ee(name)
    else:
        provincias(name)
        
    # check the tiles that intersect with the study area
    aux_coll = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterDate('2022-07-01', '2022-07-31').filterBounds(roi)

    tiles = aux_coll.aggregate_array('MGRS_TILE').getInfo()
    orbit = aux_coll.aggregate_array('SENSING_ORBIT_NUMBER').getInfo()

    tiles_orbit = list(zip(tiles, orbit))

    # calculate the tile and orbit which contains more area of the study area
    def get_area(tile_orbit):
        tile, orbit = tile_orbit
        img = aux_coll.filterMetadata('MGRS_TILE', 'equals', tile).filterMetadata('SENSING_ORBIT_NUMBER', 'equals', orbit)
        area = img.geometry().intersection(roi, ee.ErrorMargin(1)).area().getInfo()
        return area

    areas = list(map(get_area, tiles_orbit))
    areas_tiles_orbit = list(zip(areas, tiles_orbit))
    
    for area, tile_orbit in areas_tiles_orbit:
        if area == max(areas):
            tile, orbit = tile_orbit
            break
    
    print(tile, orbit)
    selected_coll = aux_coll.filterMetadata('MGRS_TILE', 'equals', tile).filterMetadata('SENSING_ORBIT_NUMBER', 'equals', orbit)
    tileShape = selected_coll.first().geometry()
    tileShape = ee.FeatureCollection(tileShape)
    # download the tile in the temporal directory
    tmp_dir = os.path.join('.', 'tmp')
    tmp_file = os.path.join(tmp_dir, f'{tile}_{orbit}.shp')
    os.makedirs(tmp_dir, exist_ok=True)
    geemap.ee_to_shp(tileShape, filename=tmp_file)
    
    return tmp_file 


def download(outdir:str, initial_date:str, end_date:str, resolution:str, index:str='NDVI'):
    global roi, tile, orbit, n_images, get_n_images, progress
    print(f"Initial date: {initial_date}, End date: {end_date}, Resolution: {resolution}, Index: {index}")
    sentinel_collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterDate(initial_date, end_date).filterMetadata('MGRS_TILE', 'equals', tile).filterMetadata('SENSING_ORBIT_NUMBER', 'equals', orbit)
    n_images = len(sentinel_collection.getInfo()['features'])
    get_n_images = True
    print(f"Number of images: {n_images}")
    
    # calculate NDVI for each image in the collection
    if index == 'NDVI':
        collection = calculate_ndvi_sentinel(sentinel_collection)
    else:
        return None
    
    # download the images
    cuts_dir = r"\\Tierra\bd_sigpac\Tiles_S2\TILES"
    cuts_dir = os.path.join(cuts_dir, tile)
    if resolution == '10':
        cuts_dir = os.path.join(cuts_dir, f'{tile}_16')
    elif resolution == '20':
        cuts_dir = os.path.join(cuts_dir, f'{tile}_4')
    elif resolution == '60':
        cuts_dir = os.path.join(cuts_dir, '60')
    print(cuts_dir) 
    # get the .shp files in the directory
    shp_files = glob.glob(os.path.join(cuts_dir, "*.shp"))
    # remove the .shp that ends with _gcs
    shp_files = [f for f in shp_files if not f.endswith("_gcs.shp")]
    c_list = []
    for f in shp_files:
        c_list.append(geemap.shp_to_ee(f))
    print(len(c_list))
    
    temp_dir = os.path.join(outdir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    images = collection.toList(len(collection.getInfo()["features"]))
    n = len(images.getInfo())
    scale = resolution
    progress = 0
    for i in range(n):
        image = ee.Image(images.get(i))
        name = image.get('system:index').getInfo()
        for c, j in zip(c_list, range(len(c_list))):
            filename = os.path.join(temp_dir, f'{name}_{j}.tif')
            geemap.ee_export_image(image, filename=filename, scale=int(scale), region=c.geometry(), file_per_band=False)
        # mossaic the n images
        filename = os.path.join(outdir, f'{name}.tif')
        # list the temp files
        temp_files = os.listdir(temp_dir)
        g = gdal.Warp(filename, [os.path.join(temp_dir, f) for f in temp_files], format='GTiff')
        g = None
        # remove the temp files
        for f in temp_files:
            os.remove(os.path.join(temp_dir, f))
        progress += 1
    
    get_n_images = False
       
        

    
    
def calculate_ndvi_sentinel(collection):
    def add_ndvi(image):
        img = image.addBands(image.normalizedDifference(['B8A', 'B4']).rename('NDVI')).select('NDVI')
        # take the quality band and delete the pixel with clouds, shadows,
        quality = image.select('QA60')
        mask = quality.bitwiseAnd(1 << 10).eq(0).And(quality.bitwiseAnd(1 << 11).eq(0))
        img = img.updateMask(mask)
        return img
    return collection.map(add_ndvi)


