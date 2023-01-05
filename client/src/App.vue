<template>
  <v-app>
    <v-main>
      <v-row no-gutters dense>
        <v-col cols="12" sm="4">
          <v-tabs
            class="is-sticky"
            bg-color="indigo-darken-2"
            fixed-tabs
            v-model="tab"
          >
            <v-tab value="route"> <v-icon start> route </v-icon> route </v-tab>
            <v-tab value="basemap">
              <v-icon start> map </v-icon> basemaps
            </v-tab>
          </v-tabs>
          <v-window v-model="tab">
            <v-window-item value="route">
              <app-home></app-home>
            </v-window-item>

            <v-window-item value="basemap">
              <app-base-maps></app-base-maps>
            </v-window-item>
          </v-window>
        </v-col>
        <v-col id="map" class="is-sticky"> </v-col>
      </v-row>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppHome from "./components/AppHome.vue";
import AppBaseMaps from "./components/AppBaseMaps.vue";
import axios from "axios";

import { ref, onMounted, onUnmounted, reactive } from "vue";
import { useAppStore } from "@/store/app";

axios.defaults.baseURL = import.meta.env.VITE_API_URL;
axios.interceptors.response.use((response) => response.data);

const appStore = useAppStore();
const tab = ref("home");


onMounted(() => {
  console.log(import.meta.env.VITE_API_URL)
  appStore.addMap();
});
onUnmounted(() => {
  appStore.removeMap();
});
</script>

<style>
#map {
  height: 100vh;
}
.is-sticky {
  z-index: 50 !important;
  position: sticky !important;
  right: 0;
  top: 0;
}
</style>
