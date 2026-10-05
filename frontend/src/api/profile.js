import http from './http'

export const getProfile = () => http.get('/profile')
export const updateProfile = (payload) => http.put('/profile', payload)
// Multipart upload (field `file`); axios sets the boundary automatically.
export const uploadAvatar = (formData) => http.post('/profile/avatar', formData)
