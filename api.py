import pandas as pd
import requests
import geopandas as gpd
import pymap3d as pm
import os
import astropy
from astropy.coordinates import EarthLocation, AltAz, get_sun
from astropy import units
import time
from datetime import datetime
import numpy as np

# https://qiita.com/phyblas/items/9a087ad1f73aca5dcbe5
# https://qiita.com/ina111/items/6e3c4d85036fd993d23c

def get_elev(lon, lat):
    x = 'http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php'
    res = requests.get(x, params=dict(lon=lon, lat=lat, outtype='JSON')).json()
    time.sleep(0.5)
    return res['elevation']

def getstainfo(staname):
    x = os.path.dirname(__file__)
    sta = pd.read_csv(x + '/all_stations.csv')
    sta = gpd.GeoDataFrame(sta, geometry=gpd.points_from_xy(sta.x, sta.y), crs=2451).to_crs(4612)
    sta = sta.sort_values('tokyo')
    ans = sta[sta.station == staname].geometry.values[0]
    return ans

def fujisan(lat=35.360556, lon=138.727778, alt=3776, staname='追浜', is_getelev=True):
    ans = getstainfo(staname)
    lon_s, lat_s = ans.x, ans.y
    alt_s = get_elev(ans.x, ans.y) if is_getelev else 0
    x,y,z = pm.geodetic2ecef(lat_s, lon_s, alt_s)
    az,el,range = pm.geodetic2aer(lat, lon, alt, lat_s, lon_s, alt_s)
    msg = f'みえる! 方位角{round(az)} 仰角{round(el, 2)}' \
        if el > 0 else f'みえない(ノω･､)うぅ… 方位角{round(az)} 仰角{round(el, 2)}'
    detail = "ECEF座標 : %d [m], %d [m], %d [m]" % (x, y, z) + \
        "\n方位角 = %.1f [deg], 仰角 = %.1f [deg], 直線距離 = %.1f [m]" % (az, el, range)
    return dict(msg=msg, detail=detail, data=[az, el, range])

def locsun(lon_s, lat_s):
    #koko = EarthLocation(lat='35 40 30.78',lon='139 32 17.1')
    koko = EarthLocation(lon=lon_s, lat=lat_s)
    toki = astropy.time.Time(datetime(2021, 12, 24, 16, 0, 0)) - 9 * units.hour + [0, 10, 20, 30, 40, 50] * units.minute
    taiyou = get_sun(toki).transform_to(AltAz(obstime=toki, location=koko))
    return taiyou.az.value, taiyou.alt.value

if __name__ == '__main__':
    print(fujisan(is_getelev=False)['msg'])