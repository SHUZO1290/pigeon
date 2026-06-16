import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const http = axios.create({ baseURL: '' })

http.isLoggingOut = false

export function setLoggingOut(state) {
  http.isLoggingOut = state
}

http.interceptors.request.use(config => {
  if (http.isLoggingOut) {
    return Promise.reject(new axios.Cancel('Logout in progress'))
  }
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  response => response,
  error => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      if (!auth.isLoggingOut) {
        auth.logout()
      }
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)

export default http