import http from './http'

export const searchFoods = (params) => http.get('/foods', { params })
