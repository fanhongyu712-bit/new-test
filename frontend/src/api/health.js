import request from './request'

export const healthApi = {
  getMetrics(params) {
    return request.get('/health/metrics', { params })
  },

  getDevices(params) {
    return request.get('/health/devices', { params })
  },

  createDevice(data) {
    return request.post('/health/devices', data)
  },

  uploadData(data) {
    return request.post('/health/data', data)
  },

  getTrend(elderlyId, params) {
    return request.get(`/health/data/${elderlyId}/trend`, { params })
  },

  getLatestData(elderlyId) {
    return request.get(`/health/data/${elderlyId}/latest`)
  }
}

export const getHealthMetrics = healthApi.getMetrics
export const getDevices = healthApi.getDevices
export const createDevice = healthApi.createDevice
export const uploadHealthData = healthApi.uploadData
export const getHealthTrend = (elderlyId, metricCode, params) => 
  request.get(`/health/data/${elderlyId}/trend`, { params: { metric_code: metricCode, ...params } })
export const getLatestHealthData = healthApi.getLatestData
