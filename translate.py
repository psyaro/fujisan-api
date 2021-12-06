import geopandas as gpd
from shapely.geometry import Point

df = gpd.read_file('var/station.geojson', epsg=4612)[['N02_003', 'N02_005', 'geometry']]
df.geometry = df.geometry.centroid
df.columns = ['railway', 'station', 'geometry']
df = df.to_crs(2451)
df['x'] = df.geometry.y.astype(int)
df['y'] = df.geometry.x.astype(int)
df['tokyo'] = df.geometry.distance(Point(-34737, -6075)).astype(int)
df = df.drop('geometry', 1)
df.to_csv('all_stations.csv', index=None)
df = df.sort_values('tokyo', ascending=True).drop('railway', 1).drop_duplicates(subset='station')
df.to_csv('stations-simplify.csv', index=None)
