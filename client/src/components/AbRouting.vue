<template>
  <div class="pa-4">
      <v-text-field
        @click:clear="errorMessages = ''"
        clearable
        v-model.trim="origin"
        label="Enter origin coord"
        variant="outlined"
        color="#3bb2d0"
      ></v-text-field>

      <v-text-field
        @click:clear="errorMessages = ''"
        clearable
        v-model.trim="destination"
        label="Enter destination coord"
        variant="outlined"
        color="#8a8acb"
      ></v-text-field
    >
    <v-alert
      v-if="errorMessages"
      :text="errorMessages"
      type="error"
      class="mb-4"
    ></v-alert>
    <v-btn
      :disabled="!destination && !destination"
      @click="getRoute"
      color="blue  elevation-0 "
    >
      Search</v-btn
    >
  </div>
  <v-progress-linear
    :active="loading"
    indeterminate
    absolute
    bottom
  ></v-progress-linear>
</template>

<script setup lang="ts">
import { ref} from "vue";
import axios from "axios";
import { useAppStore } from "@/store/app";

const appStore = useAppStore();
const loading = ref(false);
const origin = ref('');
const destination = ref("");
const errorMessages = ref("");

function getRoute() {
  loading.value = true;
  errorMessages.value = "";
  appStore.clearMap();
  appStore.clearRoutesFilter();
  axios
    .get("/route", {
      params: { origin: origin.value, destination: destination.value },
    })
    .then((new_routes) => {
      appStore.setSourceData("routes", new_routes);
      const originCoords = origin.value.split(",").map((x) => parseFloat(x));
      const destinationCoords = destination.value
        .split(",")
        .map((x) => parseFloat(x));
      appStore.setMarker(originCoords, "origin");
      appStore.setMarker(destinationCoords, "destination");
    })

    .catch((err) => {
      console.log(err);
      if (err.response.data.detail)
        errorMessages.value = err.response.data.detail;
      else errorMessages.value = "Error";
      loading.value = false;
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>
