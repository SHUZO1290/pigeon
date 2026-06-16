import http from './http'

export default {
  login: (username, password) => http.post('/auth/login', { username, password }),
  getMe: () => http.get('/auth/me'),
  impersonate: (managerId) => http.post(`/auth/impersonate/${managerId}`),
}