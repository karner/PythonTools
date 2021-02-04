
import ee
ee.Initialize()
lat = 48
lon = 17
point = {'type': 'Point', 'coordinates': [lon, lat]}
#image_collection = ee.ImageCollection("LANDSAT/LE7_L1T_32DAY_NDVI")
image_collection = ee.ImageCollection("VITO/PROBAV/S1_TOC_100M")
band = image_collection.select("NDVI")
scale = ee.Image(band.first()).projection().nominalScale().getInfo()
info = image_collection.getRegion(point, scale).getInfo()
test = 1