import http from './http'

export default {
  getTableList: () => http.get('/cash-register/tables').then(r => r.data),
  getTable: (tableId) => http.get(`/cash-register/tables/${tableId}`).then(r => r.data),
  getRows: (tableId) => http.get(`/cash-register/tables/${tableId}/rows`).then(r => r.data),
  createRow: (tableId, data) => http.post(`/cash-register/tables/${tableId}/rows`, { data }).then(r => r.data),
  updateRow: (rowId, data) => http.put(`/cash-register/rows/${rowId}`, { data }).then(r => r.data),
  deleteRow: (rowId) => http.delete(`/cash-register/rows/${rowId}`),
}