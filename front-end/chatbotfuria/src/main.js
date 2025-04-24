import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

if (process.env.NODE_ENV === 'production') {
  app.config.devtools = false
  app.config.performance = false
}

app.mount('#app')