import { createApp } from 'vue'
import App from './App.vue'
import router from "./router";
import VueTheMask from "vue-the-mask";

const app = createApp(App)

if (process.env.NODE_ENV === 'production') {
  app.config.devtools = false
  app.config.performance = false
}
app.use(router);
app.mount('#app');
app.use(VueTheMask);