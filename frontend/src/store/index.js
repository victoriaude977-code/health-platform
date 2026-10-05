import { createStore } from 'vuex'
import auth from './modules/auth'
import health from './modules/health'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    health,
    ui,
  },
})
