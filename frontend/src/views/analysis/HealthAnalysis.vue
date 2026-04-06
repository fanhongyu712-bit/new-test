<template>
  <div class="health-analysis">
    <!-- 顶部筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="选择老人">
          <el-select 
            v-model="selectedElderly" 
            placeholder="请选择老人" 
            @change="handleElderlyChange"
            filterable
            clearable
          >
            <el-option 
              v-for="item in elderlyList" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="analyzeHealth" :loading="loading">
            <el-icon><Analysis /></el-icon>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 健康风险评估 -->
    <el-row :gutter="20" v-if="riskResult">
      <el-col :span="24">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>健康风险评估结果</span>
              <el-tag :type="getRiskType(riskResult.risk_level)" effect="dark" size="large">
                {{ getRiskText(riskResult.risk_level) }}
              </el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="risk-score">
                <div class="score-value">{{ riskResult.risk_score?.toFixed(1) || 0 }}</div>
                <div class="score-label">风险评分</div>
              </div>
            </el-col>
            <el-col :span="18">
              <div class="probabilities">
                <div 
                  class="prob-item" 
                  v-for="(prob, level) in riskResult.probabilities" 
                  :key="level"
                >
                  <span class="prob-label">{{ getRiskText(level) }}</span>
                  <el-progress 
                    :percentage="((prob || 0) * 100).toFixed(1)" 
                    :color="getRiskColor(level)" 
                    :stroke-width="10" 
                  />
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider>风险因素分析</el-divider>
          
          <div class="risk-factors" v-if="riskResult.risk_factors?.length">
            <el-tag 
              v-for="factor in riskResult.risk_factors" 
              :key="factor.type" 
              :type="getSeverityType(factor.severity)"
              style="margin-right: 10px; margin-bottom: 10px;"
            >
              {{ factor.metric }}: {{ factor.value }} ({{ factor.severity }})
            </el-tag>
          </div>
          <el-empty v-else description="暂无风险因素" :image-size="60" />

          <el-divider>健康建议</el-divider>
          
          <ul class="recommendations" v-if="riskResult.recommendations?.length">
            <li v-for="rec in riskResult.recommendations" :key="rec">{{ rec }}</li>
          </ul>
          <el-empty v-else description="暂无建议" :image-size="60" />

          <div class="model-info">
            <el-tag type="info">模型: {{ riskResult.model_used }}</el-tag>
            <el-tag type="info" style="margin-left: 10px;">架构: {{ riskResult.deep_learning_architecture }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 异常检测 -->
    <el-row :gutter="20" v-if="anomalyResult" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="result-card">
          <template #header>
            <span>异常检测结果</span>
          </template>
          
          <el-result
            :icon="anomalyResult.is_anomaly ? 'error' : 'success'"
            :title="anomalyResult.is_anomaly ? '检测到异常' : '未检测到异常'"
          >
            <template #sub-title>
              <div>异常分数: {{ ((anomalyResult.anomaly_score || 0) * 100).toFixed(2) }}% (阈值: {{ ((anomalyResult.threshold || 0) * 100).toFixed(1) }}%)</div>
              <div v-if="anomalyResult.anomaly_type" style="margin-top: 10px;">
                异常类型: <el-tag type="danger">{{ anomalyResult.anomaly_type }}</el-tag>
              </div>
              <div style="margin-top: 10px;">
                <el-tag type="info">{{ anomalyResult.model_used }}</el-tag>
              </div>
            </template>
          </el-result>
        </el-card>
      </el-col>
    </el-row>

    <!-- 健康趋势预测 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="trendResult">
      <el-col :span="24">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>健康趋势预测 (未来7天)</span>
              <el-tag :type="getTrendType(trendResult.trend_direction)">
                {{ getTrendText(trendResult.trend_direction) }}
              </el-tag>
            </div>
          </template>
          
          <div ref="chartRef" class="chart"></div>
          
          <div class="model-info" style="margin-top: 20px;">
            <el-tag type="info">模型: {{ trendResult.model_used }}</el-tag>
            <el-tag type="info" style="margin-left: 10px;">{{ trendResult.deep_learning_architecture }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getElderlyList } from '@/api/elderly'
import { predictHealthRisk, detectAnomaly, predictTrend } from '@/api/ml'

const loading = ref(false)
const elderlyList = ref([])
const selectedElderly = ref('')
const riskResult = ref(null)
const anomalyResult = ref(null)
const trendResult = ref(null)
const chartRef = ref(null)
let chart = null

// 映射配置
const riskTypeMap = { low: 'success', medium: 'warning', high: 'warning', critical: 'danger' }
const riskTextMap = { low: '低风险', medium: '中等风险', high: '高风险', critical: '危急' }
const riskColorMap = { low: '#67C23A', medium: '#E6A23C', high: '#F56C6C', critical: '#F56C6C' }
const trendTypeMap = { increasing: 'danger', decreasing: 'warning', stable: 'success' }
const trendTextMap = { increasing: '上升趋势', decreasing: '下降趋势', stable: '平稳' }

const getRiskType = (level) => riskTypeMap[level] || 'info'
const getRiskText = (level) => riskTextMap[level] || level
const getRiskColor = (level) => riskColorMap[level] || '#909399'
const getTrendType = (direction) => trendTypeMap[direction] || 'info'
const getTrendText = (direction) => trendTextMap[direction] || direction
const getSeverityType = (severity) => {
  const map = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}

// 获取老人列表
const fetchElderly = async () => {
  try {
    const res = await getElderlyList({ page: 1, page_size: 100 })
    elderlyList.value = res?.items || res || []
    if (elderlyList.value.length > 0) {
      selectedElderly.value = elderlyList.value[0].id
    }
  } catch (error) {
    console.error('获取老人列表失败:', error)
  }
}

// 切换老人
const handleElderlyChange = async () => {
  riskResult.value = null
  anomalyResult.value = null
  trendResult.value = null
  
  if (selectedElderly.value) {
    await analyzeHealth()
  }
}

// 健康分析
const analyzeHealth = async () => {
  if (!selectedElderly.value) return
  
  loading.value = true
  try {
    const [riskRes, anomalyRes, trendRes] = await Promise.all([
      predictHealthRisk(selectedElderly.value),
      detectAnomaly(selectedElderly.value),
      predictTrend(selectedElderly.value, { metric: 'heart_rate' })
    ])
    
    riskResult.value = riskRes
    anomalyResult.value = anomalyRes
    trendResult.value = trendRes

    await nextTick()
    renderChart()
  } catch (error) {
    console.error('健康分析失败:', error)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!trendResult.value?.predictions || !chartRef.value) return

  if (chart) {
    chart.dispose()
    chart = null
  }
  
  chart = echarts.init(chartRef.value)

  const predictions = trendResult.value.predictions
  const dates = predictions.map(p => p.date)
  const values = predictions.map(p => p.heart_rate || p.systolic_bp || p.temperature || p.spo2 || 0)

  chart.setOption({
    title: { text: '健康指标趋势预测', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value', name: '数值' },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#409EFF' }
    }]
  })
}

// 组件卸载时清理
onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
})

// 页面加载时获取数据
onMounted(async () => {
  await fetchElderly()
  if (selectedElderly.value) {
    await analyzeHealth()
  }
})
</script>

<style scoped>
.health-analysis {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.risk-score {
  text-align: center;
  padding: 20px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
}

.score-label {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.probabilities {
  padding: 10px 20px;
}

.prob-item {
  margin-bottom: 15px;
}

.prob-label {
  display: inline-block;
  width: 80px;
  font-size: 14px;
}

.risk-factors {
  padding: 10px 0;
}

.recommendations {
  padding-left: 20px;
  line-height: 2;
}

.model-info {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.chart {
  height: 350px;
  width: 100%;
}
</style>
