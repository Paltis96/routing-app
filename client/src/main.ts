import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

import 'bulma'
import 'bulma-list/css/bulma-list.css'
import "maplibre-gl/dist/maplibre-gl.css";

const app = createApp(App)

app.use(createPinia())

app.mount('#app')
