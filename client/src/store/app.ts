// Utilities
import { defineStore } from 'pinia'
import { Map, NavigationControl, Marker } from "maplibre-gl";
import { featureEach } from '@turf/meta'
import bbox from '@turf/bbox'

export const useAppStore = defineStore('app', {
  state: () => ({
    map: {} as any,
    zoomControl: new NavigationControl({}),
    marker: new Marker(),
    markerA: new Marker({ color: '#3bb2d0' }),
    markerB: new Marker({ color: '#8a8acb' }),
    curMapSyle: 1,
    mapsTileSyles: {
      title: "Google Satellite Hybrid",
      img: "https://qms.nextgis.com/api/v1/icons/81/content",
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
              tiles: ["https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"],
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
            'fill-opacity': 0.2
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
        // routes
        this.map.addSource('routes', {
          'type': 'geojson',
          'data': {
            "type": "FeatureCollection",
            "features": []
          }
        })
        this.map.addLayer({
          'id': 'route-outline',
          'source': 'routes',
          'type': 'line',
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#0D47A1',
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
            'line-color': '#2196F3',
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
          'filter': ["==", ['get', 'location_id'], '']
        });
        // buffer
        this.map.addLayer({
          'id': 'buffer-pois',
          'type': 'circle',
          'source': 'pois_in_buffer',
          'paint': {
            'circle-stroke-width': 2,
            'circle-stroke-color': '#0D47A1',
            'circle-radius': 4.5,
            'circle-color': '#ffffff'
          },
          'filter': ['==', '$type', 'Point']
        });

        this.map.addLayer({
          'id': 'buffer-pois-labels',
          'type': 'symbol',
          'source': 'pois_in_buffer',
          'layout': {
            'text-field':
              ['to-string', ['get', 'location_id']],
            'text-size': 14,
            'text-variable-anchor': ['top'],
            "text-radial-offset": 0.5
          },
          'paint': {
            'text-halo-width': 2,
            'text-halo-color': '#ffffff'
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
    setMarker(coords: number[], type: string) {
      if (type == 'origin') {
        this.markerA.setLngLat(coords as any)
          .addTo(this.map);
      }
      else if (type == 'destination') {
        this.markerB.setLngLat(coords as any)
          .addTo(this.map);
      }
      else {
        this.marker.setLngLat(coords as any)
          .addTo(this.map);
      }
    },
    updateRoutesFilter(id: string[]) {
      const layers = ['route-outline', 'route', 'buffer-pois', 'buffer-pois-labels']
      const filter = ["in",
        ['get', 'location_id'],
        ["literal", id]]
      layers.forEach((layer) => {
        this.map.setFilter(layer, filter)
      })
    },
    clearRoutesFilter() {
      const layers = ['route-outline', 'route', 'buffer-pois', 'buffer-pois-labels']
      layers.forEach((layer) => {
        this.map.setFilter(layer, ['all'])
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
    clearMap() {
      const geojsonData = {
        "type": "FeatureCollection",
        "features": []
      };
      this.marker.remove()
      this.markerA.remove()
      this.markerB.remove()
      this.map.getSource('pois_in_buffer').setData(geojsonData)
      this.map.getSource('routes').setData(geojsonData)

    }
  }
})
