import { defineStore } from 'pinia'
import http, { setLoggingOut } from '@/api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isLoggingOut: false,
  }),
  actions: {
    async login(username, password) {
      const res = await http.post('/auth/login', { username, password })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('token', this.token)
      http.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    },
    logout() {
      this.isLoggingOut = true
      setLoggingOut(true)
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete http.defaults.headers.common['Authorization']
      window.location.href = '/login'
    },
    async impersonate(managerId) {
      const res = await http.post(`/auth/impersonate/${managerId}`)
      this.token = res.data.access_token
      this.user = res.data.user || null
      localStorage.setItem('token', this.token)
      http.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    },
    async impersonateCashier(cashierId) {
      const res = await http.post(`/auth/impersonate-cashier/${cashierId}`)
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('token', this.token)
      http.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    }
  }
})