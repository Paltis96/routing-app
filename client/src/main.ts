import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

import 'bulma'
import 'bulma-list/css/bulma-list.css'
import "maplibre-gl/dist/maplibre-gl.css";

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBZ7Wx_aIwJx22oB-DgVTB16c6e3_W35CE",
  authDomain: "routing-demo-86a47.firebaseapp.com",
  projectId: "routing-demo-86a47",
  storageBucket: "routing-demo-86a47.appspot.com",
  messagingSenderId: "556952494230",
  appId: "1:556952494230:web:ffd7136272fef6379a22b7"
};
initializeApp(firebaseConfig);


const app = createApp(App)

app.use(createPinia())

app.mount('#app')
