import pandas as pd
import requests
import geopandas as gpd
import pymap3d as pm
import os

def get_elev(lon, lat):
    x = 'http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php'
    res = requests.get(x, params=dict(lon=lon, lat=lat, outtype='JSON')).json()
    return res['elevation']

def getstainfo(staname):
    x = os.path.dirname(__file__)
    sta = pd.read_csv(x + '/all_stations.csv')
    sta = gpd.GeoDataFrame(sta, geometry=gpd.points_from_xy(sta.x, sta.y), crs=2451).to_crs(4612)
    sta = sta.sort_values('tokyo')
    ans = sta[sta.station == staname].geometry.values[0]
    return ans

def fujisan(staname):
    lat_Fuji = 35.360556 # [deg]
    lon_Fuji = 138.727778 # [deg]
    alt_Fuji = 3776 # 楕円体高 [m]
    ans = getstainfo(staname)
    lon_Kokyo, lat_Kokyo = ans.x, ans.y
    alt_Kokyo = get_elev(ans.x, ans.y)
    x,y,z = pm.geodetic2ecef(lat_Kokyo, lon_Kokyo, alt_Kokyo)
    az,el,range = pm.geodetic2aer(lat_Fuji, lon_Fuji, alt_Fuji, lat_Kokyo, lon_Kokyo, alt_Kokyo)
    msg = 'みえる！' if el > 0 else 'みえない(ノω･､)うぅ…'
    detail = "ECEF座標 : %d [m], %d [m], %d [m]" % (x, y, z) + \
        "\n方位角 = %.1f [deg], 仰角 = %.1f [deg], 直線距離 = %.1f [m]" % (az, el, range)
    return dict(msg=msg, detail=detail, data=[az, el, range])

if __name__ == '__main__':
    print(fujisan('京都')['msg'])