// Utilities
import { defineStore } from 'pinia'
import { Map, NavigationControl } from "maplibre-gl";
import { featureEach, geomEach } from '@turf/meta'
import bbox from '@turf/bbox'

export const useAppStore = defineStore('app', {
  state: () => ({
    map: {} as any,
    zoomControl: new NavigationControl({}),
    curMapSyle: 1,
    mapsTileSyles: {
      title: "OSM",
      img: "https://tile.openstreetmap.org/4/9/5.png",
    },
  }),
  actions: {
    addMap() {
      this.map = new Map({
        container: 'map',
        hash: true,
        style: {
          version: 8,
          glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
          sources: {
            __baseMap: {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
            },
          },
          layers: [
            {
              id: "__baseMap",
              type: "raster",
              source: "__baseMap",
            },
          ],
        },
        center: [56.927, 21.504],
        zoom: 6,
      });
      this.map.on('load', () => {

        this.map.addSource('pois', {
          'type': 'vector',
          'tiles': [
            `${import.meta.env.VITE_API_URL}/tiles/{z}/{x}/{y}.pbf`
          ],
          'minzoom': 6,
          'maxzoom': 14
        });
        this.map.addLayer(
          {
            'id': 'pois',
            'source': 'pois',
            'source-layer': 'default',
            'type': 'circle',
            'paint': {
              'circle-stroke-width': 1.5,
              'circle-stroke-color': '#ffffff',
              'circle-radius': 4,
              'circle-color': '#3f51b5'
            }
          },
        );
        this.map.addSource('pois_in_buffer', {
          'type': 'geojson',
          'data': {
            "type": "FeatureCollection",
            "features": []
          }
        })
        this.map.addLayer({
          'id': 'buffer-fill',
          'type': 'fill',
          'source': 'pois_in_buffer',
          'paint': {
            'fill-color': '#4CAF50',
            'fill-opacity': 0.3
          },
          'filter': ['==', '$type', 'Polygon']
        });
        this.map.addLayer({
          'id': 'buffer-line',
          'source': 'pois_in_buffer',
          'type': 'line',
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#4CAF50',
            'line-width': 2
          },
          'filter': ['==', '$type', 'Polygon']
        });
        this.map.addSource('routes', {
          'type': 'geojson',
          'data': {
            "type": "FeatureCollection",
            "features": []
          }
        })
        // routes
        this.map.addLayer({
          'id': 'route-outline',
          'source': 'routes',
          'type': 'line',
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#283593',
            'line-width': 6
          }

        });
        this.map.addLayer({
          'id': 'route',
          'source': 'routes',
          'type': 'line',
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#5c6bc0',

            'line-width': 3
          },
        });
        this.map.addLayer({
          'id': 'route-hover',
          'source': 'routes',
          'type': 'line',
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#F44336',
            'line-width': 8
          },
          'filter':["==", ['get', 'location_id'], '']
        });
        // buffer
        this.map.addLayer({
          'id': 'buffer-pois',
          'type': 'circle',
          'source': 'pois_in_buffer',
          'paint': {
            'circle-radius': 3,
            'circle-color': '#ffffff',
            'circle-stroke-width': 1.6,

          },
          'filter': ['==', '$type', 'Point']
        });
        this.map.addSource('a-point', {
          'type': 'geojson',
          'data': {
            "type": "FeatureCollection",
            "features": []
          }
        });

        this.map.addLayer({
          'id': 'a-point',
          'type': 'circle',
          'source': 'a-point',
          'paint': {
            'circle-radius': 10,
            'circle-color': '#3887be'
          }
        });
      })
      this.map.addControl(this.zoomControl, "top-right");

    },
    removeMap() {
      this.map.remove();
    },
    setSourceData(source_id: any, features: any) {
      this.map.getSource(source_id).setData(features)
      this.flyToBuffer(features)
    },

    updateRoutesFilter(id: string[]) {
      const layers = ['route-outline', 'route', 'buffer-pois']
      const filter = ["in",
        ['get', 'location_id'],
        ["literal", id]]
      layers.forEach((layer) => {
        this.map.setFilter(layer, filter)
      })
    },
    updateHoverFilter(newId: string) {
      const layer = 'route-hover'
      this.map.setFilter(layer, ["==", ['get', 'location_id'], newId])

    },
    flyToBuffer(features: any) {
      featureEach(features, (currentFeature) => {
        // @ts-ignore
        if (currentFeature.geometry.type == 'Polygon')
          this.map.fitBounds(bbox(currentFeature))
      })
    },
    setBaseMap(e: any) {
      this.mapsTileSyles.title = e.name;
      this.mapsTileSyles.img = e.icon;
      this.curMapSyle = e.id;
      this.map.getSource("__baseMap").tiles = [e.url];
      this.map.style.sourceCaches["__baseMap"].clearTiles();
      this.map.style.sourceCaches["__baseMap"].update(this.map.transform);
      this.map.triggerRepaint();
    },
  }
})
