<template>
  <v-sheet color="indigo" class="pa-4">
    <v-text-field
      @keyup.enter="getPoiInRadius"
      :loading="loading"
      variant="solo"
      hide-details="auto"
      clearable
      v-model="query"
      label="Search"
      placeholder="Enter location_id"
    ></v-text-field>
  </v-sheet>
  <v-row class="ma-2">
    <v-col cols="12">
      <v-card v-if="routesLen > 0">
        <v-card-title>Routes: {{ routesLen }}</v-card-title>
        <v-table hover fixed-header height="50vh" @mouseleave="hoverId = ''">
          <thead>
            <tr>
              <th class="text-left">
                <v-checkbox
                  density="compact"
                  hide-details="auto"
                  v-model="allSelected"
                  @click="togleSelection"
                ></v-checkbox>
              </th>
              <th class="text-left">To point</th>
              <th class="text-left">Name</th>
              <!-- <th class="text-left">id</th> -->
              <th class="text-left">type</th>
              <th class="text-left">length km</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in routesProps"
              :key="item.name"
              @mouseover="hoverId = item.location_id"
            >
              <td>
                <v-checkbox
                  density="compact"
                  hide-details="auto"
                  v-model="selectedRoutesId"
                  :value="item.location_id"
                ></v-checkbox>
              </td>
              <td>{{ item.location_id }}</td>
              <td>{{ item.location_name }}</td>
              <td>{{ item.location_type }}</td>
              <td>{{ item.length_km }}</td>
            </tr>
          </tbody>
        </v-table>
        <v-card-actions>
          <v-btn @click="downloadContent" color="indigo">
            Export to kml {{ selectedRoutesLen }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, computed, watch } from "vue";
import { useAppStore } from "@/store/app";
import axios from "axios";

// @ts-ignore
import { saveAs } from "file-saver";
// @ts-ignore
import tokml from "@maphubs/tokml";

const appStore = useAppStore();
const query = ref("");
const loading = ref(false);
const selectedRoutesId: any = ref([]);
const hoverId = ref("");
let routes: any = reactive({});

const routesLen = computed(() => {
  return routes.features ? routes.features.length : 0;
});
const selectedRoutesLen = computed(() => {
  return selectedRoutesId.value.length;
});
const allSelected = computed(() => {
  return routesLen.value == selectedRoutesLen.value;
});
const routesProps = computed(() => {
  return routes.features.map((feature: any) => feature.properties);
});
const selectedRowsGeom = computed(() => {
  const output = { ...routes };
  output.features = output.features.filter((prop: any) => {
    const id = prop.properties.location_id;
    return selectedRoutesId.value.includes(id);
  });
  return output;
});

watch(selectedRoutesId, (newId: string[]) => {
  appStore.updateRoutesFilter(newId);
});

watch(hoverId, (newId: string, ) => {
  appStore.updateHoverFilter(newId );
});
const togleSelection = () => {
  selectedRoutesId.value =
    selectedRoutesId.value.length > 0
      ? []
      : routesProps.value.map((item: any) => item.location_id);
};

const getPoiInRadius = async () => {
  loading.value = true;
  axios
    .all([
      axios.get("/get-loc", {
        params: { id: query.value },
      }),
      axios.get("/calc-routes", {
        params: { id: query.value },
      }),
    ])
    .then((res) => {
      console.log(res[1]);
      appStore.setSourceData("pois_in_buffer", res[0]);
      routes = Object.assign(routes, res[1]);
      selectedRoutesId.value = routesProps.value.map(
        (item: any) => item.location_id
      );
      appStore.setSourceData("routes", res[1]);
    })
    .catch((err) => {
      if (err.response) alert(err.response.data.detail);
    })
    .finally(() => {
      loading.value = false;
    });
};

const downloadContent = (key: any, type = "kml") => {
  const data = selectedRowsGeom.value;
  let blob;
  switch (type) {
    case "geojson":
      blob = new Blob([JSON.stringify(data)], {
        type: "application/json",
      });
      saveAs(blob, `sample.geojson`);
      break;
    case "kml":
      const newKml = tokml(data);
      blob = new Blob([newKml], {
        type: "application/xml",
      });
      saveAs(blob, `sample.kml`);
      break;
    default:
      break;
  }
};
</script>
