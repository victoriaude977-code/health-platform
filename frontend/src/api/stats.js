import http from './http'

export const getDailyStats = (date) => http.get('/stats/daily', { params: { date } })
export const getTrends = (days) => http.get('/stats/trends', { params: { days } })
export const getMonthly = (months) => http.get('/stats/monthly', { params: { months } })
