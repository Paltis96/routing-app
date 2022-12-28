CREATE OR REPLACE FUNCTION cp_NearestNode(IN point geometry) RETURNS BIGINT  
AS $BODY$
BEGIN 
  RETURN id
  FROM ways_vertices_pgr
  ORDER BY ST_Transform(the_geom, 23240) <-> point
  LIMIT 1;
END $BODY$ LANGUAGE 'plpgsql';