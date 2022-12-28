from fastapi import FastAPI, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .db import db

ORIGINS = [
    '*'
    # "http://devmaps.xyz",
    # "https://devmaps.xyz",
    # "http://localhost",
    # "http://localhost:8080",
]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await db.get_pool()


@app.on_event("shutdown")
async def shutdown_event():
    await db.close_pool()


@app.get("/get-loc", status_code=status.HTTP_200_OK)
async def get_loc(id: str, conn=Depends(db.connection)):

    sql_q = """SELECT to_jsonb( t.* ) - 'id' - 'geom' AS json FROM locations t WHERE location_id = $1"""
    res = await conn.fetchval(sql_q, id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return res


@app.get("/get-route", status_code=status.HTTP_200_OK)
async def get_loc(id: str, conn=Depends(db.connection)):

    sql_q = """SELECT routes FROM routes WHERE location_id = $1"""
    res = await conn.fetchval(sql_q, id)
    if not res:
       return None
    return res

async def sent_task(conn, sql, id):
    await conn.execute(sql, id)

@app.post("/calc-route", status_code=status.HTTP_200_OK)
async def get_loc(id: str, background_tasks: BackgroundTasks, conn=Depends(db.connection)):
    
    route = await conn.fetchval("""SELECT routes FROM routes WHERE location_id = $1""",id)
    if route:
        print(route)
        return
    
    await conn.execute("""INSERT INTO routes(location_id)  VALUES($1) on conflict do nothing""",id)
    sql_q = """--sql
        UPDATE routes
        SET routes = res.routes
        FROM (WITH input_point AS (
            SELECT 
			Location_Name
			, Lat
			, Long
			, Location_Type
			, Note
            , location_id
			, ST_Transform(geom, 23240) AS geom 
            FROM public.locations 
            WHERE location_id = $1),
        buffer AS (
            SELECT ST_Buffer(geom, 5000) AS geom 
            FROM input_point
        ),
		res AS (
			SELECT 
        cp_FromAtoB(t3.geom, ST_Transform(t1.geom, 23240),23240, to_jsonb(t3) - 'geom') as obj
                FROM public.locations t1 , buffer t2, input_point t3
                WHERE ST_Intersects(t2.geom, ST_Transform(t1.geom, 23240)) 
                AND t1.location_id <> $1
                LIMIT 3
            )
        SELECT jsonb_build_object(
        'type', 'FeatureCollection',
        'features', jsonb_agg(obj)) as routes
        FROM res, input_point t2) res
        WHERE routes.location_id = $1
        """
    background_tasks.add_task(sent_task, conn, sql_q, id)




@app.get("/tiles/{z}/{x}/{y}.pbf", status_code=status.HTTP_200_OK)
async def get_loc(z: int, x: int, y: int, conn=Depends(db.connection)):

    sql_q = """--sql
    WITH mvtgeom AS
    (
        SELECT ST_AsMVTGeom(ST_Transform(geom, 3857), ST_TileEnvelope($1, $2, $3), extent => 4096, buffer => 64) AS geom,   location_id,
                    location_name
        FROM locations
        WHERE ST_Transform(geom, 3857) && ST_TileEnvelope($1, $2, $3, margin => (64.0 / 4096))
    )
    SELECT ST_AsMVT(mvtgeom.*) as tiles
    FROM mvtgeom;
    """
    res = await conn.fetchval(sql_q, z, x, y)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(content=res, media_type="application/octet-stream")
