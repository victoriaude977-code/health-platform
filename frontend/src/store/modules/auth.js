// Auth module: JWT token (persisted in localStorage) and the current user.
import * as authApi from '@/api/auth'

const state = {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
}

const getters = {
  isAuthenticated: (s) => Boolean(s.token),
  token: (s) => s.token,
  user: (s) => s.user,
}

const mutations = {
  SET_TOKEN(s, token) {
    s.token = token
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  },
  SET_USER(s, user) {
    s.user = user
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  },
}

const actions = {
  async login({ commit }, payload) {
    const { data } = await authApi.login(payload)
    commit('SET_TOKEN', data.access_token)
    commit('SET_USER', data.user)
    return data.user
  },
  async register({ commit }, payload) {
    const { data } = await authApi.register(payload)
    commit('SET_TOKEN', data.access_token)
    commit('SET_USER', data.user)
    return data.user
  },
  async fetchMe({ commit }) {
    const { data } = await authApi.fetchMe()
    commit('SET_USER', data.user)
    return data.user
  },
  logout({ commit }) {
    commit('SET_TOKEN', '')
    commit('SET_USER', null)
  },
}

export default { namespaced: true, state, getters, mutations, actions }
