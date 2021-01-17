import { createApp } from "vue";
import App from "./App.vue";
import "./assets/tailwind.css";
import "./assets/style.css";
import router from "./router";
import VueSnap from "vue-snap";
import "vue-snap/dist/vue-snap.css";

createApp(App)
  .use(router)
  .use(VueSnap)
  .mount("#app");
