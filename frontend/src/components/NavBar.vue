<template>
  <header class="navbar">
    <div class="brand" @click="$router.push('/')">
      <svg class="logo" viewBox="0 0 32 32">
        <rect width="32" height="32" rx="7" fill="#14B8A6" />
        <path d="M6 17h4l3-8 5 14 3-6h5" fill="none" stroke="#fff" stroke-width="2.6"
          stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="brand-name">HealthPlatform</span>
    </div>

    <!-- Desktop navigation: compact pill links (replaces the full-width
         el-menu that stretched across half the header). -->
    <nav class="nav-links">
      <button v-for="item in navItems" :key="item.path" type="button"
        class="nav-link" :class="{ active: activeMenu === item.path }"
        @click="$router.push(item.path)">
        {{ item.label }}
      </button>
    </nav>

    <div class="nav-right">
      <el-tooltip :content="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
        placement="bottom">
        <el-button circle class="theme-btn" aria-label="Toggle theme"
          @click="store.dispatch('ui/toggleTheme')">
          <el-icon><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
        </el-button>
      </el-tooltip>

      <el-dropdown @command="onCommand" class="user-dropdown">
        <span class="user-chip">
          <UserAvatar :avatar="user && user.avatar" :username="user ? user.username : ''"
            :size="30" />
          <span class="username">{{ user ? user.username : '' }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon> Profile
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon> Log out
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- Mobile: hamburger opens the drawer -->
      <el-button circle class="theme-btn burger" aria-label="Open menu"
        @click="drawerOpen = true">
        <el-icon><Menu /></el-icon>
      </el-button>
    </div>

    <!-- Mobile navigation drawer -->
    <el-drawer v-model="drawerOpen" direction="rtl" size="78%" :with-header="false">
      <div class="drawer-inner">
        <div class="drawer-user">
          <UserAvatar :avatar="user && user.avatar" :username="user ? user.username : ''"
            :size="46" />
          <div>
            <div class="drawer-name">{{ user ? user.username : '' }}</div>
            <div class="drawer-email muted">{{ user ? user.email : '' }}</div>
          </div>
        </div>

        <nav class="drawer-links">
          <button v-for="item in navItems" :key="item.path" type="button"
            class="drawer-link" :class="{ active: activeMenu === item.path }"
            @click="go(item.path)">
            {{ item.label }}
          </button>
        </nav>

        <div class="drawer-footer">
          <el-button class="drawer-theme" @click="store.dispatch('ui/toggleTheme')">
            <el-icon style="margin-right: 6px">
              <Moon v-if="!isDark" /><Sunny v-else />
            </el-icon>
            {{ isDark ? 'Light theme' : 'Dark theme' }}
          </el-button>
          <el-button class="drawer-theme" @click="go('/profile')">
            <el-icon style="margin-right: 6px"><User /></el-icon> Profile
          </el-button>
          <el-button type="danger" plain class="drawer-theme" @click="logout">
            <el-icon style="margin-right: 6px"><SwitchButton /></el-icon> Log out
          </el-button>
        </div>
      </div>
    </el-drawer>
  </header>
</template>

<script>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'NavBar',
  components: { UserAvatar },
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const drawerOpen = ref(false)

    const user = computed(() => store.getters['auth/user'])
    const isDark = computed(() => store.getters['ui/isDark'])
    const activeMenu = computed(() => '/' + (route.path.split('/')[1] || ''))

    const navItems = [
      { path: '/', label: 'Dashboard' },
      { path: '/meals', label: 'Meals' },
      { path: '/workouts', label: 'Workouts' },
      { path: '/charts', label: 'Charts' },
      { path: '/recommendations', label: 'For You' },
      { path: '/goal', label: 'Goal' },
    ]

    const go = (path) => {
      drawerOpen.value = false
      router.push(path)
    }

    const logout = () => {
      drawerOpen.value = false
      store.dispatch('auth/logout')
      router.push('/login')
    }

    const onCommand = (cmd) => {
      if (cmd === 'logout') logout()
      else if (cmd === 'profile') router.push('/profile')
    }

    return { store, user, isDark, activeMenu, navItems, drawerOpen, go, onCommand }
  },
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  gap: 18px;
  background: var(--surface);
  border-bottom: 1px solid var(--border-strong);
  padding: 0 24px;
  height: 58px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
}

.logo {
  width: 28px;
  height: 28px;
}

.brand-name {
  font-weight: 700;
  font-size: 16px;
  color: var(--ink-strong);
  letter-spacing: 0.2px;
}

.nav-links {
  display: flex;
  gap: 4px;
  margin-left: 12px;
}

.nav-link {
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  color: var(--ink-soft);
  padding: 7px 14px;
  border-radius: 999px;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}

.nav-link:hover {
  background: var(--border);
  color: var(--ink-strong);
}

.nav-link.active {
  background: var(--brand);
  color: #fff;
  font-weight: 600;
}

.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.theme-btn {
  border: 1px solid var(--border-strong);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.username {
  color: var(--ink-soft);
  font-size: 14px;
}

.burger {
  display: none;
}

/* Drawer (mobile menu) */
.drawer-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.drawer-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 4px 18px;
  border-bottom: 1px solid var(--divider);
}

.drawer-name {
  font-weight: 600;
  color: var(--ink-strong);
}

.drawer-email {
  font-size: 12.5px;
  margin-top: 2px;
}

.drawer-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 0;
}

.drawer-link {
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 15px;
  text-align: left;
  color: var(--ink-soft);
  padding: 12px 12px;
  border-radius: 10px;
  transition: background 0.15s;
}

.drawer-link:hover {
  background: var(--border);
}

.drawer-link.active {
  background: var(--brand);
  color: #fff;
  font-weight: 600;
}

.drawer-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--divider);
}

.drawer-theme {
  width: 100%;
  margin-left: 0;
}

/* Phones: hide pills + username, show hamburger */
@media (max-width: 768px) {
  .navbar {
    padding: 0 12px;
    height: 54px;
  }

  .brand-name {
    font-size: 15px;
  }

  .nav-links,
  .username,
  .user-dropdown {
    display: none;
  }

  .burger {
    display: inline-flex;
  }
}
</style>
