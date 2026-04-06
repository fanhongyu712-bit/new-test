<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon elderly">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_elderly }}</div>
              <div class="stat-label">在住老人</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon alerts">
              <el-icon :size="32"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_alerts }}</div>
              <div class="stat-label">今日预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_alerts }}</div>
              <div class="stat-label">待处理预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon critical">
              <el-icon :size="32"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.critical_alerts }}</div>
              <div class="stat-label">危急预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>风险分布</span>
            </div>
          </template>
          <div ref="riskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>预警级别分布</span>
            </div>
          </template>
          <div ref="alertChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="table-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最新预警</span>
              <el-button type="primary" link @click="router.push('/alerts')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="latestAlerts" style="width: 100%">
            <el-table-column prop="title" label="预警标题" show-overflow-tooltip />
            <el-table-column prop="alert_level" label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.alert_level)">
                  {{ getAlertLevelText(row.alert_level) }}
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
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>高风险老人</span>
              <el-button type="primary" link @click="router.push('/elderly')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="highRiskElderly" style="width: 100%">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="room_number" label="房间" width="80" />
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.risk_level)">
                  {{ getAlertLevelText(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewElderly(row.id)">
                  详情
                </el-button>
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
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { reportApi } from '@/api/report'
import { alertApi } from '@/api/alert'

const router = useRouter()

const stats = ref({
  total_elderly: 0,
  today_alerts: 0,
  pending_alerts: 0,
  critical_alerts: 0
})

const latestAlerts = ref([])
const highRiskElderly = ref([])

const riskChartRef = ref(null)
const alertChartRef = ref(null)
let riskChart = null
let alertChart = null

const alertLevelMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '危急'
}

const alertTypeMap = {
  low: 'info',
  medium: 'warning',
  high: 'warning',
  critical: 'danger'
}

const getAlertLevelText = (level) => alertLevelMap[level] || level
const getAlertType = (level) => alertTypeMap[level] || 'info'
const formatTime = (time) => dayjs(time).format('MM-DD HH:mm')

const viewElderly = (id) => {
  router.push(`/elderly/${id}`)
}

const fetchDashboardData = async () => {
  try {
    const response = await reportApi.getDashboard()
    stats.value = response
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

const fetchLatestAlerts = async () => {
  try {
    const response = await alertApi.getList({ page_size: 5 })
    latestAlerts.value = response?.items || []
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
  }
}

const fetchHealthOverview = async () => {
  try {
    const response = await reportApi.getHealthOverview()
    const { risk_distribution } = response || {}
    
    highRiskElderly.value = []
    
    updateRiskChart(risk_distribution)
  } catch (error) {
    console.error('Failed to fetch health overview:', error)
  }
}

const fetchAlertStatistics = async () => {
  try {
    const response = await reportApi.getAlertStatistics()
    updateAlertChart(response?.by_level || {})
  } catch (error) {
    console.error('Failed to fetch alert statistics:', error)
  }
}

const initCharts = () => {
  if (riskChartRef.value) {
    riskChart = echarts.init(riskChartRef.value)
  }
  if (alertChartRef.value) {
    alertChart = echarts.init(alertChartRef.value)
  }
}

const updateRiskChart = (data) => {
  if (!riskChart) return
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '风险分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: data.low || 0, name: '低风险', itemStyle: { color: '#67c23a' } },
          { value: data.medium || 0, name: '中风险', itemStyle: { color: '#e6a23c' } },
          { value: data.high || 0, name: '高风险', itemStyle: { color: '#f56c6c' } },
          { value: data.critical || 0, name: '危急', itemStyle: { color: '#f56c6c' } }
        ]
      }
    ]
  }
  
  riskChart.setOption(option)
}

const updateAlertChart = (data) => {
  if (!alertChart) return
  
  const chartData = Object.entries(data).map(([key, value]) => ({
    value,
    name: alertLevelMap[key] || key
  }))
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: chartData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  alertChart.setOption(option)
}

const handleResize = () => {
  riskChart?.resize()
  alertChart?.resize()
}

onMounted(() => {
  initCharts()
  fetchDashboardData()
  fetchLatestAlerts()
  fetchHealthOverview()
  fetchAlertStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  riskChart?.dispose()
  alertChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 20px;
}

.stat-icon.elderly {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.alerts {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.critical {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-row {
  margin-bottom: 20px;
}
</style>
