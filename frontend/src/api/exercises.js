import http from './http'

export const searchExercises = (params) => http.get('/exercises', { params })
