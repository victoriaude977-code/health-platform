import http from './http'

export const logWorkout = (payload) => http.post('/workouts', payload)
export const getWorkouts = (date) => http.get('/workouts', { params: { date } })
export const deleteWorkout = (id) => http.delete(`/workouts/${id}`)
