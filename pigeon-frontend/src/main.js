import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './store/auth'
import http from './api/http'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import './global.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

const token = localStorage.getItem('token')
if (token) {
  http.defaults.headers.common['Authorization'] = `Bearer ${token}`
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const auth = useAuthStore()
    auth.user = {
      id: payload.sub,
      role: payload.role,
      username: ''
    }
    auth.token = token
  } catch (e) {
    console.error('Invalid token')
    localStorage.removeItem('token')
    delete http.defaults.headers.common['Authorization']
  }
}

app.mount('#app')