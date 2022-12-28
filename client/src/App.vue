<template>
  <div class="columns m-0">
    <div class="column is-two-fifths">
      <div class="field has-addons">
        <div class="control is-expanded">
          <input class="input" v-model="searchMessage" type="text" placeholder="Find a repository">

        </div>
        <div class="control " v-if="searchMessage">
          <a class="button is-info is-outlined" @click="getLoc">
            Search
          </a>
        </div>
      </div>
      <div v-if="qRes">
        <table class="table is-bordered is-striped is-narrow is-hoverable is-fullwidth">
          <thead>
            <tr>
              <th>key</th>
              <th>Val</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(key, item, index) in qRes">
              <td>{{ item }}</td>
              <td> {{ key }}</td>
            </tr>
          </tbody>
        </table>
        <p class="buttons">
          <button @click="calcRoute" :class="['button is-info', loading ? 'is-loading' : '']">Calc routes</button>
          <button @click="fly(qRes! as Res)" class="button is-info is-outlined">
            Fly to
          </button>
          <button class="button is-danger is-outlined">
            <span @click="qRes = null">✕</span>
          </button>
        </p>
        <h3> Routes</h3>
        <div v-if="routes" class="list">
          <div v-for="feature in routes.features" class="list-item">
            <div class="list-item-content">
              <div class="list-item-title"></div>
              <div class="list-item-description">
                <li v-for="(item, key)  in feature.properties"><b>{{ key }}</b> : {{ item }}</li>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="column p-0">
      <AppMapVue :new-source="routes" :fly-to="flyTo" />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppMapVue from './components/AppMap.vue';
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import axios from 'axios';

const searchMessage = ref('')
type Res = {
  lat: number
  long: number
  note?: string
  location_id: string
  location_name: string
  location_type: string
}
const BASE_URL = 'http://104.248.241.63:8000'
const qRes: Ref<Res> | Ref<null> = ref(null)
const flyTo: Ref<number[]> = ref([])
const routes: Ref<any> = ref(null)
const loading = ref(false)
const fly = (coord: Res) => {
  flyTo.value = [coord.long, coord.lat]

}

async function delay(ms: number) {
  // return await for better async stack trace support in case of errors.
  return await new Promise(resolve => setTimeout(resolve, ms));
}

const getLoc = async () => {
  try {
    const res = await axios.get(BASE_URL + '/get-loc', { params: { id: searchMessage.value } });
    qRes.value = res.data;
  }
  catch (error) { console.log(error); qRes.value = null }
}
const calcRoute = async () => {
  loading.value = true
  try {
    await axios.post(BASE_URL + '/calc-route', null, { params: { id: searchMessage.value } });
    while (true) {
      await delay(2000);
      const res = await axios.get(BASE_URL + '/get-route', { params: { id: searchMessage.value } });
      console.log(res)
      if (res.data) {
        routes.value = res.data
        break
      }
    }
  }
  catch (error) { console.log(error) }
  finally {
    loading.value = false
  }
}
</script>

<style lang="scss">
@import url('https://cdn-uicons.flaticon.com/uicons-bold-straight/css/uicons-bold-straight.css');

body {
  margin: 0;
  padding: 0;
}

.fi::before {
  position: relative;
  top: 2px;
}

.list {
  max-height: 45vh;
  overflow: auto;
}
</style>