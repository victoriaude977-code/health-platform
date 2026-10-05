// UI module: theme preference (light/dark), persisted and applied to <html>.
// Element Plus dark mode activates through the `dark` class on <html> plus its
// dark css-vars stylesheet (imported in main.js).
const STORAGE_KEY = 'theme'

function initialTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark' || saved === 'light') return saved
  // First visit: respect the device preference.
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// Apply (or remove) the dark class and the native color-scheme hint.
export function applyTheme(theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
  document.documentElement.style.colorScheme = theme
}

const state = {
  theme: initialTheme(),
}

const getters = {
  theme: (s) => s.theme,
  isDark: (s) => s.theme === 'dark',
}

const mutations = {
  SET_THEME(s, theme) {
    s.theme = theme
    localStorage.setItem(STORAGE_KEY, theme)
    applyTheme(theme)
  },
}

const actions = {
  initTheme({ state }) {
    applyTheme(state.theme)
  },
  toggleTheme({ state, commit }) {
    commit('SET_THEME', state.theme === 'dark' ? 'light' : 'dark')
  },
  setTheme({ commit }, theme) {
    if (theme === 'dark' || theme === 'light') commit('SET_THEME', theme)
  },
}

export default { namespaced: true, state, getters, mutations, actions }
