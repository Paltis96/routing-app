from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware

import psycopg
from psycopg.rows import dict_row

from .config import get_settings
from .db import get_loc_sql, near_locations_sql, calc_routes_sql, tile_sql
from .utils import valhalla_geojson_routes

ORIGINS = ['*']
app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch(sql, *args):
    async with await psycopg.AsyncConnection.connect(get_settings().dsn) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(sql, *args)
            return await acur.fetchall()


@app.get("/get-loc", status_code=status.HTTP_200_OK)
async def get_loc(id: str):
    res = await fetch(get_loc_sql, (id,))
    res = res[0]
    if not res['data']['features']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='location_id not exists')
    return res['data']


@app.get("/near-locations", status_code=status.HTTP_200_OK)
async def near_locations(id: str, radius: int = 5000):
    res = await fetch(near_locations_sql, {'radius': radius, 'id': id})
    res = res[0]
    if not res['data']['features']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='location_id not exists')
    return res['data']


@app.get("/routes", status_code=status.HTTP_200_OK)
async def calc_routes(lat: float, lon: float):
    start_point = {'lat': lat, 'lon': lon}
    end_pois = await fetch(calc_routes_sql, start_point)
    res = await valhalla_geojson_routes(start_point, end_pois)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return res


@app.get("/tiles/{z}/{x}/{y}.pbf", status_code=status.HTTP_200_OK)
async def get_loc(z: int, x: int, y: int, ):
    res = await fetch(tile_sql, {'z': z, "x": x, "y": y})
    res = res[0]
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(content=res['tiles'], media_type="application/octet-stream")
