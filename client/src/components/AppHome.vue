<template>
  <v-row class="ma-2" dense>
    <v-col cols="12">
      <v-card class="rounded-lg elevation-0">
        <v-card-text>
          <v-btn-toggle
            class="rounded-lg"
            v-model="routingMode"
            rounded="0"
            group
          >
            <v-btn value="route"> A/B route </v-btn>
            <v-btn value="matrix"> Matrix </v-btn>
          </v-btn-toggle>
        </v-card-text>
        <RoutingMatrix v-if="routingMode == 'matrix'" />
        <AbRouting v-if="routingMode == 'route'" />
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref } from "vue";
import RoutingMatrix from "./RoutingMatrix.vue";
import AbRouting from "./AbRouting.vue";
const routingMode = ref("matrix");
</script>
