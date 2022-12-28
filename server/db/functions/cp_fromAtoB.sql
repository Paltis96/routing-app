CREATE OR REPLACE FUNCTION cp_FromAtoB(
  IN g1 geometry, 
  IN g2 geometry, IN epsg INTEGER
)
    RETURNS SETOF jsonb
    LANGUAGE 'plpgsql'
    STABLE PARALLEL SAFE
AS $BODY$ 
DECLARE
    point_a geometry := g1;
    point_b geometry := g2;
    bbox geometry := (SELECT cp_ExtendedBbox(
          ST_Collect(point_a, point_b), (
            5000
          )::int, epsg
    ));
BEGIN 
RETURN QUERY 
WITH route AS (SELECT
      seq
    , id
    , cost_s
    , length_m
    , CASE
          WHEN node = source THEN ST_AsText(the_geom)
          ELSE ST_AsText(ST_Reverse(the_geom))
      END AS route_readable,

      CASE
          WHEN node = source THEN the_geom
          ELSE ST_Reverse(the_geom)
      END AS route_geom FROM pgr_bdDijkstra(
    'SELECT
          id
        , source
        , target
        , cost_s * priority AS cost
        , reverse_cost_s * priority AS reverse_cost
    FROM ways
    LEFT JOIN ways_configuration
    USING (tag_id)
    WHERE 
    '''|| bbox::text ||'''::geometry
     && ST_Transform(the_geom,'||epsg||')',
    (SELECT cp_NearestNode(g1)), --A
    (SELECT cp_NearestNode(g2)), --B
    true
) d
LEFT JOIN ways ON edge = id),
    agg_route AS (
        SELECT 
              floor(sum(cost_s)) AS duration_s
            , floor(sum(length_m)) AS distance_m
            , ST_LineMerge(ST_Union(route_geom)) AS geom
        FROM route
    ),
    prettier AS (
        SELECT
              duration_s
            , distance_m
            , geom
--             , ST_LineLocatePoint(geom, cp_PointWGS(lng1, lat1)) AS point_a
--             , ST_LineLocatePoint(geom, cp_PointWGS(lng2, lat2)) AS point_b
        FROM agg_route
        
    )
SELECT jsonb_build_object(
    'type',       'Feature',
--     'id',         id,
    'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb( t.* ) - 'geom'
    ) AS json
FROM prettier t;

END;
$BODY$;