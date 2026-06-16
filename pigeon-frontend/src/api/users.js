import http from './http'

export default {
  getManagers: () => http.get('/users/managers').then(r => r.data),
  createManager: (data) =>
    http.post('/users/managers', { ...data, role: 'manager' }).then(r => r.data),
  getCashiers: () => http.get('/users/cashiers').then(r => r.data),
  createCashier: (data) =>
    http.post('/users/cashiers', { ...data, role: 'cashier' }).then(r => r.data),
  deleteCashier: (id) => http.delete(`/users/cashiers/${id}`),  // если есть эндпоинт
}