// Health module: the active goal and today's dashboard data, shared across
// Dashboard / Meals / Workouts / Charts views.
import * as goalsApi from '@/api/goals'
import * as statsApi from '@/api/stats'
import * as mealsApi from '@/api/meals'
import * as workoutsApi from '@/api/workouts'

const state = {
  activeGoal: null,
  daily: null,        // /stats/daily payload
  todayMeals: [],
  todayWorkouts: [],
}

const getters = {
  activeGoal: (s) => s.activeGoal,
  daily: (s) => s.daily,
}

const mutations = {
  SET_GOAL(s, goal) { s.activeGoal = goal },
  SET_DAILY(s, daily) { s.daily = daily },
  SET_MEALS(s, meals) { s.todayMeals = meals },
  SET_WORKOUTS(s, workouts) { s.todayWorkouts = workouts },
}

const actions = {
  async fetchGoal({ commit }) {
    const { data } = await goalsApi.getGoals()
    commit('SET_GOAL', data.active_goal)
    return data.active_goal
  },
  async fetchDaily({ commit }, date) {
    const { data } = await statsApi.getDailyStats(date)
    commit('SET_DAILY', data)
    return data
  },
  async fetchTodayMeals({ commit }, date) {
    const { data } = await mealsApi.getMeals(date)
    commit('SET_MEALS', data.items)
    return data.items
  },
  async fetchTodayWorkouts({ commit }, date) {
    const { data } = await workoutsApi.getWorkouts(date)
    commit('SET_WORKOUTS', data.items)
    return data.items
  },
  async refreshToday({ dispatch }, date) {
    // Refresh all dashboard data for one date (used after logging/deleting).
    await Promise.all([
      dispatch('fetchGoal'),
      dispatch('fetchDaily', date),
      dispatch('fetchTodayMeals', date),
      dispatch('fetchTodayWorkouts', date),
    ])
  },
}

export default { namespaced: true, state, getters, mutations, actions }
