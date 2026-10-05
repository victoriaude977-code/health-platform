import http from './http'

export const logMeal = (payload) => http.post('/meals', payload)
export const getMeals = (date) => http.get('/meals', { params: { date } })
export const updateMeal = (id, payload) => http.put(`/meals/${id}`, payload)
export const deleteMeal = (id) => http.delete(`/meals/${id}`)
