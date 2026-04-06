<template>
  <div class="elderly-detail">
    <el-page-header @back="router.back()">
      <template #content>
        <span class="page-title">{{ elderlyInfo.name }} - 健康档案</span>
      </template>
    </el-page-header>
    
    <el-row :gutter="20" class="content-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ elderlyInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ elderlyInfo.gender }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ calculateAge(elderlyInfo.birth_date) }}岁</el-descriptions-item>
            <el-descriptions-item label="血型">{{ elderlyInfo.blood_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="身高">{{ elderlyInfo.height ? elderlyInfo.height + 'cm' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="体重">{{ elderlyInfo.weight ? elderlyInfo.weight + 'kg' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="房间">{{ elderlyInfo.room_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="床位">{{ elderlyInfo.bed_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="入住日期">{{ formatDate(elderlyInfo.admission_date) }}</el-descriptions-item>
          </el-descriptions>
          
          <div class="info-section">
            <h4>慢性病史</h4>
            <el-tag
              v-for="disease in elderlyInfo.chronic_diseases"
              :key="disease.name"
              type="warning"
              class="disease-tag"
            >
              {{ disease.name }}
            </el-tag>
            <span v-if="!elderlyInfo.chronic_diseases?.length">无</span>
          </div>
          
          <div class="info-section">
            <h4>过敏史</h4>
            <el-tag
              v-for="allergy in elderlyInfo.allergies"
              :key="allergy.name"
              type="danger"
              class="disease-tag"
            >
              {{ allergy.name }}
            </el-tag>
            <span v-if="!elderlyInfo.allergies?.length">无</span>
          </div>
        </el-card>
        
        <el-card shadow="hover" class="risk-card">
          <template #header>
            <span>风险评估</span>
          </template>
          <div class="risk-content">
            <div class="risk-level" :class="riskAssessment.risk_level">
              <span class="risk-value">{{ getRiskText(riskAssessment.risk_level) }}</span>
            </div>
            <div class="risk-score">
              风险评分: {{ riskAssessment.risk_score?.toFixed(1) || 0 }}
            </div>
          </div>
          
          <div v-if="riskAssessment.risk_factors?.length" class="risk-factors">
            <h4>风险因素</h4>
            <ul>
              <li v-for="(factor, index) in riskAssessment.risk_factors" :key="index">
                {{ factor.metric || factor.name }} - {{ factor.type === 'metric_high' ? '偏高' : factor.type === 'metric_low' ? '偏低' : '' }}
              </li>
            </ul>
          </div>
          
          <div v-if="riskAssessment.recommendations?.length" class="recommendations">
            <h4>健康建议</h4>
            <ul>
              <li v-for="(rec, index) in riskAssessment.recommendations" :key="index">
                {{ rec }}
              </li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>健康指标趋势</span>
              <el-select v-model="selectedMetric" placeholder="选择指标" @change="fetchHealthTrend">
                <el-option label="心率" value="heart_rate" />
                <el-option label="收缩压" value="systolic_bp" />
                <el-option label="舒张压" value="diastolic_bp" />
                <el-option label="体温" value="temperature" />
                <el-option label="血氧" value="spo2" />
              </el-select>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
        
        <el-card shadow="hover" class="latest-data-card">
          <template #header>
            <span>最新健康数据</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6" v-for="(data, code) in latestHealthData" :key="code">
              <div class="metric-card">
                <div class="metric-name">{{ data.name }}</div>
                <div class="metric-value">{{ data.value?.toFixed(1) }}</div>
                <div class="metric-unit">{{ data.unit }}</div>
                <div class="metric-time">{{ formatTime(data.time) }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>历史预警</span>
              <el-button type="primary" link @click="router.push('/alerts')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="alertHistory" style="width: 100%">
            <el-table-column prop="title" label="预警标题" show-overflow-tooltip />
            <el-table-column prop="alert_level" label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.alert_level)">
                  {{ getAlertLevelText(row.alert_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { elderlyApi } from '@/api/elderly'
import { healthApi } from '@/api/health'
import { alertApi } from '@/api/alert'

const route = useRoute()
const router = useRouter()

const elderlyId = route.params.id
const elderlyInfo = ref({})
const riskAssessment = ref({})
const latestHealthData = ref({})
const alertHistory = ref([])
const selectedMetric = ref('heart_rate')

const trendChartRef = ref(null)
let trendChart = null

const riskLevelMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '危急'
}

const alertLevelMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '危急'
}

const alertTypeMap = {
  low: 'success',
  medium: 'warning',
  high: 'warning',
  critical: 'danger'
}

const statusMap = {
  pending: '待处理',
  processing: '处理中',
  resolved: '已解决',
  false_alarm: '误报'
}

const statusTypeMap = {
  pending: 'danger',
  processing: 'warning',
  resolved: 'success',
  false_alarm: 'info'
}

const getRiskText = (level) => riskLevelMap[level] || '未评估'
const getAlertLevelText = (level) => alertLevelMap[level] || level
const getAlertType = (level) => alertTypeMap[level] || 'info'
const getStatusText = (status) => statusMap[status] || status
const getStatusType = (status) => statusTypeMap[status] || 'info'

const calculateAge = (birthDate) => {
  if (!birthDate) return '-'
  return dayjs().diff(dayjs(birthDate), 'year')
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('MM-DD HH:mm')
}

const fetchElderlyInfo = async () => {
  try {
    const response = await elderlyApi.getById(elderlyId)
    elderlyInfo.value = response
  } catch (error) {
    console.error('Failed to fetch elderly info:', error)
  }
}

const fetchRiskAssessment = async () => {
  try {
    const response = await alertApi.getRiskAssessment(elderlyId)
    riskAssessment.value = response
  } catch (error) {
    console.error('Failed to fetch risk assessment:', error)
  }
}

const fetchLatestHealthData = async () => {
  try {
    const response = await healthApi.getLatestData(elderlyId)
    latestHealthData.value = response
  } catch (error) {
    console.error('Failed to fetch latest health data:', error)
  }
}

const fetchHealthTrend = async () => {
  try {
    const response = await healthApi.getTrend(elderlyId, selectedMetric.value)
    updateTrendChart(response)
  } catch (error) {
    console.error('Failed to fetch health trend:', error)
  }
}

const fetchAlertHistory = async () => {
  try {
    const response = await alertApi.getList({
      elderly_id: elderlyId,
      page_size: 5
    })
    alertHistory.value = response?.items || []
  } catch (error) {
    console.error('Failed to fetch alert history:', error)
  }
}

const initTrendChart = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
}

const updateTrendChart = (data) => {
  if (!trendChart || !data) return
  
  const trendData = data.data || data
  const times = (trendData || []).map(d => dayjs(d.time).format('MM-DD HH:mm'))
  const values = (trendData || []).map(d => d.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: data.unit || ''
    },
    series: [
      {
        name: data.metric_name,
        type: 'line',
        smooth: true,
        data: values,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  initTrendChart()
  fetchElderlyInfo()
  fetchRiskAssessment()
  fetchLatestHealthData()
  fetchHealthTrend()
  fetchAlertHistory()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.elderly-detail {
  padding: 0;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
}

.content-row {
  margin-top: 20px;
}

.info-section {
  margin-top: 20px;
}

.info-section h4 {
  margin-bottom: 10px;
  color: #606266;
}

.disease-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.risk-card {
  margin-top: 20px;
}

.risk-content {
  text-align: center;
  padding: 20px 0;
}

.risk-level {
  display: inline-block;
  padding: 10px 30px;
  border-radius: 8px;
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.risk-level.low {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.risk-level.medium {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.risk-level.high {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.risk-level.critical {
  background: linear-gradient(135deg, #f56c6c 0%, #c45656 100%);
}

.risk-score {
  margin-top: 10px;
  font-size: 16px;
  color: #606266;
}

.risk-factors,
.recommendations {
  margin-top: 20px;
}

.risk-factors h4,
.recommendations h4 {
  margin-bottom: 10px;
  color: #606266;
}

.risk-factors ul,
.recommendations ul {
  padding-left: 20px;
}

.risk-factors li,
.recommendations li {
  margin-bottom: 5px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.latest-data-card {
  margin-top: 20px;
}

.metric-card {
  text-align: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.metric-name {
  font-size: 14px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 5px 0;
}

.metric-unit {
  font-size: 12px;
  color: #909399;
}

.metric-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 5px;
}
</style>
