get_loc_sql = """--sql
    WITH buffer AS ( 
        SELECT 
            location_id
            , ST_Transform(
                ST_Buffer(
                    ST_Transform(geom, 23240), 5000
                    ),4326) AS buffer_geom
            , geom
        FROM locations 
        WHERE location_id = %s
    ), 
    un_geoms AS (
        SELECT location_id, buffer_geom as geom
        FROM buffer
        UNION 
        SELECT t1.location_id, t1.geom
        FROM locations t1, buffer t2 
        WHERE ST_Intersects(t1.geom, t2.buffer_geom)
    )
    SELECT 
    jsonb_build_object(
        'type', 'FeatureCollection',
        'features', jsonb_agg(obj)
        ) as data
    FROM (SELECT ST_AsGeoJSON(un.*)::jsonb as obj FROM un_geoms un) t
    """
    
near_locations_sql = """--sql
    WITH buffer AS ( 
        SELECT 
            location_id
            , ST_Transform(
                ST_Buffer(
                    ST_Transform(geom, 23240), %(radius)s
                    ),4326) AS buffer_geom
            , geom
        FROM locations 
        WHERE location_id = %(id)s
    ), 
    un_geoms AS (
        SELECT NULL AS location_id, buffer_geom as geom
        FROM buffer
        UNION 
        SELECT t1.location_id, t1.geom
        FROM locations t1, buffer t2 
        WHERE ST_Intersects(t1.geom, t2.buffer_geom)
    )
    SELECT 
    jsonb_build_object(
        'type', 'FeatureCollection',
        'features', jsonb_agg(obj)
        ) as data
    FROM (SELECT ST_AsGeoJSON(un.*)::jsonb as obj FROM un_geoms un) t
    """
    
calc_routes_sql = """--sql
    WITH input_point AS (
        SELECT ST_SetSRID(ST_Point(%(lon)s, %(lat)s),4326) AS geom 
    ),
    buffer AS (
        SELECT ST_Transform(ST_Buffer(ST_Transform(geom, 23240), 5000),4326) AS geom 
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
        public.locations t1, buffer t2, input_point t3
    WHERE ST_Intersects(t2.geom, t1.geom) 
    AND NOT ST_Intersects(t3.geom, t1.geom) 
        """
        
tile_sql = """--sql
WITH mvtgeom AS
(
    SELECT 
        ST_AsMVTGeom(ST_Transform(geom, 3857)
        , ST_TileEnvelope(%(z)s, %(x)s, %(y)s)
        , extent => 4096, buffer => 64) AS geom
        , location_id
        , location_name
    FROM locations
    WHERE ST_Transform(geom, 3857) && ST_TileEnvelope(%(z)s, %(x)s, %(y)s, margin => (64.0 / 4096))
)
SELECT ST_AsMVT(mvtgeom.*) as tiles
FROM mvtgeom;
"""