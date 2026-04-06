import request from './request'

export const reportApi = {
  getDashboard(institutionId) {
    return request.get('/reports/dashboard', {
      params: { institution_id: institutionId }
    })
  },

  getAlertStatistics(params) {
    return request.get('/reports/alerts/statistics', { params })
  },

  getInterventionStatistics(params) {
    return request.get('/reports/interventions/statistics', { params })
  },

  getHealthOverview(institutionId) {
    return request.get('/reports/health/overview', {
      params: { institution_id: institutionId }
    })
  }
}

export const getDashboardStats = reportApi.getDashboard
export const getAlertStatistics = reportApi.getAlertStatistics
export const getInterventionStatistics = reportApi.getInterventionStatistics
export const getHealthOverview = reportApi.getHealthOverview
