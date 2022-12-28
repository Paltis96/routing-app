CREATE OR REPLACE FUNCTION cp_GetNearestOrders(
  	  IN lng NUMERIC
	, IN lat NUMERIC
	, IN stores_limit INT DEFAULT 5 
	, IN items_limit INT DEFAULT 5

)
    RETURNS SETOF jsonb
    LANGUAGE 'plpgsql'
    STABLE PARALLEL SAFE
AS $BODY$ 
DECLARE
BEGIN
RETURN QUERY 
WITH stock_in_stores AS (
		SELECT	
              storage_id 
			, storage_name
			, full_adress
            , geom
	 		, stock_id
			, product_id
			, quantity
			, dist_m
       FROM (
		   SELECT 
              storage_id 
			, storage_name
            , geom
			, CASE 
				WHEN city IS NOT NULL THEN district || ', '
				ELSE district END ||
			  CASE 
				WHEN street IS NOT NULL THEN city || ', '
				ELSE city END ||
			 CASE 
				WHEN house_number IS NOT NULL THEN street || ', '
				ELSE street END || house_number AS full_adress
            , floor(geom::geography
              <-> cp_PointWGS(lng, lat)::geography)::int AS dist_m
        FROM storages
		ORDER BY dist_m
        LIMIT stores_limit
	   ) o
		LEFT JOIN public.stocks st USING (storage_id) 
        WHERE quantity > 0
    ),
	nn_orders AS (
	SELECT 
		      customer_id
			, customer_name
			, o.geom
			, o.full_adress
			, item_id
			, o.product_id
			, o.quantity
			, storage_id
			, o.dist_m
	FROM stock_in_stores ss
	CROSS JOIN LATERAL (
        SELECT 
              customer_id
			, customer_name
			, geom
			, CASE 
				WHEN city IS NOT NULL THEN district || ', '
				ELSE district END ||
			  CASE 
				WHEN street IS NOT NULL THEN city || ', '
				ELSE city END ||
			 CASE 
				WHEN house_number IS NOT NULL THEN street || ', '
				ELSE street END || house_number AS full_adress
			, item_id
			, product_id
			, quantity
			, floor(ss.geom::geography <-> c.geom::geography)::int as dist_m
        FROM customers c
 		LEFT JOIN (SELECT * FROM order_basket WHERE is_complete = FALSE) ob USING (customer_id)
		LEFT JOIN (SELECT * FROM order_items WHERE is_complete = FALSE) oi USING (basket_id) 
		WHERE ss.product_id = oi.product_id
		ORDER BY dist_m
		LIMIT items_limit
    	) o
	),
	agg_stores AS (
		SELECT
			  storage_id 
			, storage_name
			, full_adress
            , geom
			, jsonb_agg(jsonb_build_object(
				 'stock_id', 	stock_id
				,'product_id',  product_id
            	,'quantity', 	quantity
			)) as product
			, dist_m
		FROM stock_in_stores
		GROUP BY 
			  storage_id
			, storage_name
			, full_adress
            , geom
			, dist_m
	),
	agg_dist AS (
		SELECT
		customer_id
		, jsonb_agg(jsonb_build_object(
				'storage_id',  storage_id
            	,'dist_m', 	dist_m
			)) as dist_m
		FROM (SELECT DISTINCT ON (customer_id, storage_id) 
			  customer_id, storage_id, dist_m 
			  FROM nn_orders) orders
		GROUP BY customer_id
	),
	agg_orders AS (
		SELECT 
			  customer_id
			, customer_name
			, geom
			, full_adress
			, jsonb_agg(jsonb_build_object(
				 'item_id', 	item_id
				,'product_id',  product_id
            	,'quantity', 	quantity
			)) as product
		, d.dist_m
			FROM (SELECT DISTINCT ON (customer_id, item_id) * FROM nn_orders) orders
		LEFT JOIN agg_dist d USING (customer_id)
		GROUP BY 
			  customer_id 
			, customer_name
			, full_adress
            , geom
		,d.dist_m
	)
    SELECT
         jsonb_build_object(
         'customer_orders', (SELECT jsonb_build_object(
                            'type', 'FeatureCollection',
                            'features', json_agg(ST_AsGeoJSON(t.*)::jsonb))
                            FROM agg_orders t),
         'storages',        (SELECT jsonb_build_object(
                            'type', 'FeatureCollection',
                            'features', json_agg(ST_AsGeoJSON(t2.*)::jsonb))
                            FROM agg_stores t2)
                            );

END;
$BODY$;