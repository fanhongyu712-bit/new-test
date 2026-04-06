import request from './request'

export const alertApi = {
  getRules(params) {
    return request.get('/alerts/rules', { params })
  },

  createRule(data) {
    return request.post('/alerts/rules', data)
  },

  updateRule(id, isActive) {
    return request.put(`/alerts/rules/${id}`, null, {
      params: { is_active: isActive }
    })
  },

  getList(params) {
    return request.get('/alerts', { params })
  },

  getById(id) {
    return request.get(`/alerts/${id}`)
  },

  handleAlert(id, handleResult) {
    return request.put(`/alerts/${id}/handle`, null, {
      params: { handle_result: handleResult }
    })
  },

  getRiskAssessment(elderlyId) {
    return request.get(`/alerts/risk-assessment/${elderlyId}`)
  }
}

export const getAlertRules = alertApi.getRules
export const createAlertRule = alertApi.createRule
export const updateAlertRule = alertApi.updateRule
export const getAlertList = alertApi.getList
export const getAlertById = alertApi.getById
export const handleAlertApi = alertApi.handleAlert
export const getRiskAssessment = alertApi.getRiskAssessment
export const getInterventionRecords = (params) => request.get('/interventions/records', { params })
