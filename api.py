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

def get_required_fuji_alt(lat_s, lon_s, alt_s, lat_f=35.360556, lon_f=138.727778):
    # 二分探索で仰角が0度になる富士山の標高を求める
    low = 0.0
    high = 100000.0  # 100km
    for _ in range(20):
        mid = (low + high) / 2
        _, el, _ = pm.geodetic2aer(lat_f, lon_f, mid, lat_s, lon_s, alt_s)
        if el > 0:
            high = mid
        else:
            low = mid
    return low

def fujisan(lat=35.360556, lon=138.727778, alt=3776, staname='追浜', is_getelev=True):
    ans = getstainfo(staname)
    lon_s, lat_s = ans.x, ans.y
    alt_s = get_elev(ans.x, ans.y) if is_getelev else 0
    x,y,z = pm.geodetic2ecef(lat_s, lon_s, alt_s)
    az,el,range = pm.geodetic2aer(lat, lon, alt, lat_s, lon_s, alt_s)
    
    # 富士山の麓（標高0m）の仰角の計算
    _, el_bottom, _ = pm.geodetic2aer(lat, lon, 0.0, lat_s, lon_s, alt_s)
    
    visible = bool(el > 0)
    
    # 露出境界標高の計算（地平線に隠れる標高）
    visible_bottom_alt = get_required_fuji_alt(lat_s, lon_s, alt_s, lat, lon)
    
    required_alt_diff = 0
    visible_percent = 0.0
    
    if visible:
        bot_alt = max(0.0, visible_bottom_alt)
        visible_percent = max(0.0, min(100.0, ((3776.0 - bot_alt) / 3776.0) * 100.0))
    else:
        required_alt_diff = int(round(visible_bottom_alt - 3776))
        visible_percent = 0.0
        
    # 平面直角座標系第IX系（9系）適用外の警告フラグ（直線距離150km以上）
    imprecise = bool(range > 150000)
    
    msg = f'みえる! 方位角{round(az)} 仰角{round(el, 2)}' \
        if visible else f'みえない(ノω･､)うぅ… 方位角{round(az)} 仰角{round(el, 2)}'
    detail = "ECEF座標 : %d [m], %d [m], %d [m]" % (x, y, z) + \
        "\n方位角 = %.1f [deg], 仰角 = %.1f [deg], 直線距離 = %.1f [m]" % (az, el, range)
        
    dist_km = float(range) / 1000
    analogies = [
        f"東京タワー約 {round(range / 333):,} 個分",
        f"フルマラソン約 {round(dist_km / 42.195, 1)} 回分",
        f"徒歩で約 {round(dist_km / 4, 1)} 時間（不眠不休）"
    ]
    
    return dict(
        msg=msg, 
        detail=detail, 
        data=[float(az), float(el), float(range)],
        visible=visible,
        station_name=staname,
        station_alt=round(float(alt_s), 1),
        required_alt_diff=required_alt_diff,
        distance_km=round(dist_km, 1),
        analogies=analogies,
        visible_percent=round(visible_percent, 1),
        visible_bottom_alt=round(float(visible_bottom_alt), 1),
        imprecise=imprecise,
        el_bottom=round(float(el_bottom), 3)
    )

def get_stations_list():
    x = os.path.dirname(__file__)
    df = pd.read_csv(x + '/stations-simplify.csv')
    return sorted(df['station'].dropna().unique().tolist())
