<template>
  <div class="elderly-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>老人列表</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加老人
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="在住" value="active" />
            <el-option label="离住" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchElderlyList">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="elderlyList" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column label="年龄" width="80">
          <template #default="{ row }">
            {{ calculateAge(row.birth_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="room_number" label="房间" width="80" />
        <el-table-column prop="bed_number" label="床位" width="80" />
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)">
              {{ getRiskText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在住' : '离住' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入住时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.admission_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">详情</el-button>
            <el-button type="primary" link @click="editElderly(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteElderly(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchElderlyList"
        @current-change="fetchElderlyList"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑老人信息' : '添加老人'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="elderlyForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="elderlyForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="elderlyForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="elderlyForm.birth_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="elderlyForm.id_card" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="血型">
              <el-select v-model="elderlyForm.blood_type" placeholder="请选择">
                <el-option label="A型" value="A" />
                <el-option label="B型" value="B" />
                <el-option label="AB型" value="AB" />
                <el-option label="O型" value="O" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身高(cm)">
              <el-input-number v-model="elderlyForm.height" :min="50" :max="250" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="elderlyForm.weight" :min="20" :max="200" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="房间号">
              <el-input v-model="elderlyForm.room_number" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="床位号">
              <el-input v-model="elderlyForm.bed_number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入住日期">
              <el-date-picker
                v-model="elderlyForm.admission_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="慢性病史">
          <el-input
            v-model="chronicDiseasesText"
            type="textarea"
            :rows="2"
            placeholder="请输入慢性病史，多个用逗号分隔"
          />
        </el-form-item>
        
        <el-form-item label="过敏史">
          <el-input
            v-model="allergiesText"
            type="textarea"
            :rows="2"
            placeholder="请输入过敏史，多个用逗号分隔"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { elderlyApi } from '@/api/elderly'

const router = useRouter()

const loading = ref(false)
const elderlyList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const elderlyForm = reactive({
  name: '',
  gender: '男',
  birth_date: '',
  id_card: '',
  blood_type: '',
  height: null,
  weight: null,
  room_number: '',
  bed_number: '',
  admission_date: '',
  chronic_diseases: [],
  allergies: []
})

const chronicDiseasesText = computed({
  get: () => elderlyForm.chronic_diseases?.map(d => d.name).join(', ') || '',
  set: (val) => {
    elderlyForm.chronic_diseases = val.split(',').filter(Boolean).map(name => ({ name: name.trim() }))
  }
})

const allergiesText = computed({
  get: () => elderlyForm.allergies?.map(a => a.name).join(', ') || '',
  set: (val) => {
    elderlyForm.allergies = val.split(',').filter(Boolean).map(name => ({ name: name.trim() }))
  }
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birth_date: [{ required: true, message: '请选择出生日期', trigger: 'change' }]
}

const riskLevelMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '危急'
}

const riskTypeMap = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  critical: 'danger'
}

const getRiskText = (level) => riskLevelMap[level] || '未评估'
const getRiskType = (level) => riskTypeMap[level] || 'info'

const calculateAge = (birthDate) => {
  if (!birthDate) return '-'
  return dayjs().diff(dayjs(birthDate), 'year')
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const fetchElderlyList = async () => {
  loading.value = true
  try {
    const response = await elderlyApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    })
    elderlyList.value = response?.items || []
    pagination.total = response?.total || 0
  } catch (error) {
    ElMessage.error('获取老人列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.name = ''
  searchForm.status = ''
  pagination.page = 1
  fetchElderlyList()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(elderlyForm, {
    name: '',
    gender: '男',
    birth_date: '',
    id_card: '',
    blood_type: '',
    height: null,
    weight: null,
    room_number: '',
    bed_number: '',
    admission_date: '',
    chronic_diseases: [],
    allergies: []
  })
  dialogVisible.value = true
}

const editElderly = (row) => {
  isEdit.value = true
  Object.assign(elderlyForm, {
    ...row,
    birth_date: row.birth_date ? new Date(row.birth_date) : '',
    admission_date: row.admission_date ? new Date(row.admission_date) : ''
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          ...elderlyForm,
          birth_date: elderlyForm.birth_date ? dayjs(elderlyForm.birth_date).format('YYYY-MM-DD') : null,
          admission_date: elderlyForm.admission_date ? dayjs(elderlyForm.admission_date).format('YYYY-MM-DD') : null
        }
        
        if (isEdit.value) {
          await elderlyApi.update(elderlyForm.id, data)
          ElMessage.success('更新成功')
        } else {
          await elderlyApi.create(data)
          ElMessage.success('添加成功')
        }
        
        dialogVisible.value = false
        fetchElderlyList()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
      }
    }
  })
}

const deleteElderly = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该老人信息吗？', '提示', {
      type: 'warning'
    })
    await elderlyApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchElderlyList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewDetail = (id) => {
  router.push(`/elderly/${id}`)
}

onMounted(() => {
  fetchElderlyList()
})
</script>

<style scoped>
.elderly-list {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
