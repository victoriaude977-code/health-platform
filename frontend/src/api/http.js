// Shared Axios instance: base URL /api (proxied to Flask in dev), JWT header
// injected from the Vuex auth module, and automatic logout on 401.
import axios from 'axios'
import store from '@/store'

const http = axios.create({
  baseURL: '/api',
  timeout: 20000,
})

http.interceptors.request.use((config) => {
  const token = store.getters['auth/token']
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response && error.response.status
    if (status === 401 && store.getters['auth/isAuthenticated']) {
      store.dispatch('auth/logout')
    }
    return Promise.reject(error)
  }
)

// Uniform error-message extractor for view code.
export function errorMessage(err, fallback = 'Something went wrong') {
  const data = err && err.response && err.response.data
  return (data && data.error) || (err && err.message) || fallback
}

export default http
