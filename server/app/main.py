from fastapi import FastAPI, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
import json
import psycopg
from psycopg.rows import dict_row

from .config import get_settings


ORIGINS = ['*']
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get-loc", status_code=status.HTTP_200_OK)
async def get_loc(id: str, ):
    sql_q = """SELECT 
                location_name
                ,location_id
                ,lat
                ,long
                ,location_type,note
                FROM locations WHERE location_id = %s
                """
    async with await psycopg.AsyncConnection.connect(get_settings().dsn) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(sql_q, (id,))
            res = await acur.fetchone()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return res


async def valhalla_get(json):
    async with aiohttp.ClientSession() as session:
        async with session.post( 'http://valhalla:8002/route', data=json) as resp:
            return await resp.json()


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


@app.get("/calc-routes", status_code=status.HTTP_200_OK)
async def calc_routes(id: str):
    sql_1 = """SELECT lat, long as lon FROM locations WHERE location_id = %(id)s"""
    sql_q = """--sql
        WITH input_point AS (
            SELECT 
			Location_Name
			, Lat
			, Long
			, Location_Type
			, Note
            , location_id
			, ST_Transform(geom, 23240) AS geom 
            FROM public.locations 
            WHERE location_id = %(id)s),
        buffer AS (
            SELECT ST_Transform(ST_Buffer(geom, 5000),4326) AS geom 
            FROM input_point
        )
		SELECT 
            t1.Location_Name
			, t1.Location_Type
			, t1.Note
            , t1.location_id
            , st_x(t1.geom) as lon
            , st_y(t1.geom) as lat
        FROM 
            public.locations t1, buffer t2
        WHERE ST_Intersects(t2.geom, t1.geom) 
        AND t1.location_id <> %(id)s
            """

    async with await psycopg.AsyncConnection.connect(get_settings().dsn) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(sql_1, {'id': id})
            sart_poi = await acur.fetchone()
            await acur.execute(sql_q, {'id': id})
            end_pois = await acur.fetchall()

    fc = {
        "type": "FeatureCollection",
        "features": []}

    for end in end_pois:
        q = {"locations": [sart_poi, {'lon': end['lon'], 'lat': end['lat']}],
             "costing": "auto",
             "directions_options": {"units": "kilometers"}}
        res = await valhalla_get(json.dumps(q))
        geojson = {
            "type": "Feature",
                    "properties": {**end,
                                   'time': res['trip']['summary']['time'],
                                   'length_km': res['trip']['summary']['length'],
                                   },
                    "geometry": {
                        "coordinates": decode_route(res['trip']['legs'][0]['shape']),
                        "type": "LineString"
                    }}
        fc['features'].append(geojson)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return fc


@app.get("/tiles/{z}/{x}/{y}.pbf", status_code=status.HTTP_200_OK)
async def get_loc(z: int, x: int, y: int, ):

    sql_q = """--sql
    WITH mvtgeom AS
    (
        SELECT ST_AsMVTGeom(ST_Transform(geom, 3857), ST_TileEnvelope(%(z)s, %(x)s, %(y)s), extent => 4096, buffer => 64) AS geom,   location_id,
                    location_name
        FROM locations
        WHERE ST_Transform(geom, 3857) && ST_TileEnvelope(%(z)s, %(x)s, %(y)s, margin => (64.0 / 4096))
    )
    SELECT ST_AsMVT(mvtgeom.*) as tiles
    FROM mvtgeom;
    """
    async with await psycopg.AsyncConnection.connect(get_settings().dsn) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(sql_q, {'z': z, "x": x, "y": y})
            res = await acur.fetchone()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(content=res['tiles'], media_type="application/octet-stream")
