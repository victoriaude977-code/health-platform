import http from './http'

export const getGoals = () => http.get('/goals')
export const createGoal = (payload) => http.post('/goals', payload)
export const updateGoal = (id, payload) => http.put(`/goals/${id}`, payload)
export const deleteGoal = (id) => http.delete(`/goals/${id}`)
