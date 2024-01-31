import geemap
import ee
import os
import sys
import numpy as np
from osgeo import gdal, ogr, osr
import glob
import time

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
    global roi
    
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


def download(oudir:str, initial_date:str, end_date:str, resolution:int):
    global roi
    pass

    
    
    
