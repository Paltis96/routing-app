<template>
  <div ref="mapContainer" class="hero  is-fullheight"></div>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted, ref } from "vue";
import { Map, NavigationControl, Popup } from "maplibre-gl";

// TODO
let BASE_URL = ''
const prod = import.meta.env.PROD
if (prod) {
  BASE_URL = 'http://104.248.241.63:8000'
}
else {
  BASE_URL = 'http://api:8000'
}

const props = defineProps(['flyTo', 'newSource'])

const mapContainer = ref(null);
let map: any

onMounted(() => {
  map = new Map({
    container: mapContainer.value!,
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
    center: [57.3474, 20.3456],
    zoom: 5,
  });
  map.on('load', () => {
    map.addSource('locatoins', {
      'type': 'vector',
      'tiles': [
        `${BASE_URL}/tiles/{z}/{x}/{y}.pbf`
      ],
      'minzoom': 7,
      'maxzoom': 15
    });
    map.addSource('routes', {
      type: 'geojson',
      data: {
        "type": "FeatureCollection",
        "features": []
      }
    });
    map.addLayer(
      {
        'id': 'locatoins',
        'type': 'circle',
        'source': 'locatoins',
        'source-layer': 'default',
        'paint': {
          'circle-radius': 3,
          'circle-color': '#3887be'
        }
      },
    ); map.addLayer({
      'id': 'routes',
      'type': 'line',
      'source': 'routes',
      'layout': {
        'line-join': 'round',
        'line-cap': 'round'
      },
      'paint': {
        'line-color': '#888',
        'line-width': 8
      }
    });
  });
});

watch(() => props.newSource!, (newSource) => {
  if (newSource && Object.keys(newSource).length > 0)
    map.getSource('routes').setData(newSource)
})

watch(() => props.flyTo!, (x) => {
  console.log(`x is ${x}`)
  map.flyTo({
    center: x,
    zoom: 14
  });
})

onUnmounted(() => {
  map.removeMap;
});
</script>

