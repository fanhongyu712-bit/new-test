import request from './request'

export const mlApi = {
  getModelInfo() {
    return request.get('/ml/model-info')
  },

  predictHealthRisk(elderlyId) {
    return request.get(`/ml/health-risk/${elderlyId}`)
  },

  detectAnomaly(elderlyId) {
    return request.get(`/ml/anomaly-detection/${elderlyId}`)
  },

  predictTrend(elderlyId, params) {
    return request.get(`/ml/trend-prediction/${elderlyId}`, { params })
  },

  batchRiskAssessment(institutionId) {
    return request.get('/ml/batch-risk-assessment', {
      params: { institution_id: institutionId }
    })
  }
}

export const getModelInfo = mlApi.getModelInfo
export const predictHealthRisk = mlApi.predictHealthRisk
export const detectAnomaly = mlApi.detectAnomaly
export const predictTrend = mlApi.predictTrend
export const batchRiskAssessment = mlApi.batchRiskAssessment
