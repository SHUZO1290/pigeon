import http from './http'

export default {
  getPoints: () => http.get('/points/').then(r => r.data),
  getPoint: (id) => http.get(`/points/${id}`).then(r => r.data),
  createPoint: (data) =>
    http.post('/points/', {
      name: data.name,
      address: data.address || '',
      manager_id: data.manager_id
    }).then(r => r.data),
  createTable: (pointId, name) =>
    http.post(`/tables/points/${pointId}`, { name }).then(r => r.data),
  getCashiers: () => http.get('/users/cashiers').then(r => r.data),
  assignCashier: (pointId, cashierId) =>
    http.post(`/points/${pointId}/cashiers/${cashierId}`),
}