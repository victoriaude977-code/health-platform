<template>
  <el-config-provider>
    <div v-if="isAuthPage" class="auth-layout">
      <router-view />
      <el-button circle class="auth-theme-btn" aria-label="Toggle theme"
        @click="toggleTheme">
        <el-icon><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
      </el-button>
    </div>
    <!-- Plain flex column: el-container/el-header are avoided here because
         Element Plus mis-detected the component-wrapped header and rendered
         the main area in a row (content pushed right, empty center). -->
    <div v-else class="app-layout">
      <NavBar />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: { NavBar },
  setup() {
    const store = useStore()
    const route = useRoute()
    const isAuthPage = computed(() => ['login', 'register'].includes(route.name))
    const isDark = computed(() => store.getters['ui/isDark'])
    const toggleTheme = () => store.dispatch('ui/toggleTheme')
    return { isAuthPage, isDark, toggleTheme }
  },
}
</script>

<style>
.auth-theme-btn {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.35);
  color: #fff;
}

.auth-theme-btn:hover {
  background: rgba(255, 255, 255, 0.24);
  color: #fff;
}
</style>
