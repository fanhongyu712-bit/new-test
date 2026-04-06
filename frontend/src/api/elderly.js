import request from './request'

export const elderlyApi = {
  getList(params) {
    return request.get('/elderly', { params })
  },

  getById(id) {
    return request.get(`/elderly/${id}`)
  },

  create(data) {
    return request.post('/elderly', data)
  },

  update(id, data) {
    return request.put(`/elderly/${id}`, data)
  },

  delete(id) {
    return request.delete(`/elderly/${id}`)
  },

  getHealthRecords(id, params) {
    return request.get(`/elderly/${id}/health-records`, { params })
  },

  createHealthRecord(id, data) {
    return request.post(`/elderly/${id}/health-records`, data)
  }
}

export const getElderlyList = elderlyApi.getList
export const getElderlyById = elderlyApi.getById
export const createElderly = elderlyApi.create
export const updateElderly = elderlyApi.update
export const deleteElderly = elderlyApi.delete
export const getHealthRecords = elderlyApi.getHealthRecords
export const createHealthRecord = elderlyApi.createHealthRecord
