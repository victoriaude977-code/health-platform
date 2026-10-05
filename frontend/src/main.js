import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// Dark-mode css variables (activated by the `dark` class on <html>).
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import store from './store'
import './assets/global.css'

// Apply the saved theme before mounting to avoid a light-mode flash.
store.dispatch('ui/initTheme')

const app = createApp(App)

// Register all Element Plus icons globally (used as <el-icon><Plus/></el-icon>).
for (const [name, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(name, component)
}

app.use(store)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
