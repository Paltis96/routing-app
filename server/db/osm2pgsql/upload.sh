osm2pgsql --slim --drop --output=flex --style=./routes.lua -H 0.0.0.0 -P 5432 -d app -U postgres -W ./gcc-states-latest.osm.pbf