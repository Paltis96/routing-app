
import aiohttp
import asyncio
import json


def decode_route(encoded):
    inv = 1.0 / 1e6
    decoded = []
    previous = [0, 0]
    i = 0
    # for each byte
    while i < len(encoded):
        # for each coord (lat, lon)
        ll = [0, 0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            # keep decoding bytes until you have this coord
            while byte >= 0x20:
                byte = ord(encoded[i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            # get the final value adding the previous offset and remember it for the next
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j]
                                   & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        # scale by the precision and chop off long coords also flip the positions so
        # its the far more standard lon,lat instead of lat,lon
        decoded.append([float('%.6f' % (ll[1] * inv)),
                        float('%.6f' % (ll[0] * inv))])
    # hand back the list of coordinates
    return decoded


async def valhalla_get(json):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://valhalla:8002/route', data=json) as resp:
            return await resp.json()


async def valhalla_geojson_route(sart_poi, end_poi):
    fc = {
        "type": "FeatureCollection",
        "features": []}
    q = {"locations": [sart_poi, end_poi],
         "costing": "auto",
         "directions_options": {"units": "kilometers"}}
    res = await valhalla_get(json.dumps(q))
    time = res['trip']['summary']['time']
    length_km = res['trip']['summary']['length']
    geom = res['trip']['legs'][0]['shape']
    geojson = {
        "type": "Feature",
        "properties": {
            'time': time,
            'length_km': length_km,
        },
        "geometry": {
            "coordinates": decode_route(geom),
            "type": "LineString"
        }}
    fc['features'].append(geojson)
    return fc

async def valhalla_geojson_routes(sart_poi, end_pois):

    fc = {
        "type": "FeatureCollection",
        "features": []}

    for end in end_pois:
        q = {"locations": [sart_poi, {'lon': end['lon'], 'lat': end['lat']}],
             "costing": "auto",
             "directions_options": {"units": "kilometers"}}
        res = await valhalla_get(json.dumps(q))
        time = res['trip']['summary']['time']
        length_km = res['trip']['summary']['length']
        geom = res['trip']['legs'][0]['shape']
        geojson = {
            "type": "Feature",
            "id": end['location_id'],
            "properties": {**end,
                           'time': time,
                           'length_km': length_km,
                           },
            "geometry": {
                "coordinates": decode_route(geom),
                "type": "LineString"
            }}
        fc['features'].append(geojson)

    def get_key(e):
        return e['properties']['length_km']

    fc['features'].sort(key=get_key)

    return fc
