from pydantic import BaseSettings
import psycopg


class Settings(BaseSettings):
    dsn: str

    class Config:
        env_file = ".env"


with psycopg.connect(Settings().dsn) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT tablename FROM pg_catalog.pg_tables WHERE tablename = 'locations';""")
        res = cur.fetchone()
        if res:
            exit()
            
        cur.execute("""--sql
            CREATE TABLE public.locations (
            id serial primary key ,
            location_name text,
            location_id text,
            lat double precision,
            long double precision,
            location_type text,
            note text,
            geom geometry
            );
            """)
        conn.commit()

        with open('locations.sql') as sql:
            cur.execute(sql.read())

        cur.execute("""CREATE INDEX ON public.locations USING GIST (geom);""")
