import http from './http'

export default {
  getOwnerDashboard: () => http.get('/dashboard/owner').then(r => r.data),
  getManagerDashboard: () => http.get('/dashboard/manager').then(r => r.data),
  getCashierDashboard: () => http.get('/dashboard/cashier').then(r => r.data),
}