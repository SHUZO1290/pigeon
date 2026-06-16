import http from './http'

export default {
  getTable: (tableId) => http.get(`/tables/${tableId}`).then(r => r.data),
  addColumn: (tableId, colData) =>
    http.post(`/tables/${tableId}/columns`, colData).then(r => r.data),
  deleteColumn: (columnId) => http.delete(`/tables/columns/${columnId}`),
  deleteTable: (tableId) => http.delete(`/tables/${tableId}`)

}