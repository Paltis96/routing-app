
CREATE OR REPLACE FUNCTION cp_ExtendedBbox(
     IN collected_geom geometry
   , IN units_to_expand INT
   , in epsg INT
   , OUT bbox geometry)   
AS $BODY$
  SELECT ST_Expand(
             ST_Transform(
                 ST_Envelope(
                        collected_geom
                    )  
                 ,epsg)
            , units_to_expand);
$BODY$ LANGUAGE 'sql';