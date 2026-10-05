import http from './http'

export const getRecommendations = (type, limit = 5) =>
  http.get('/recommendations', { params: { type, limit } })
export const getRecommendationHistory = (type) =>
  http.get('/recommendations/history', { params: type ? { type } : {} })
