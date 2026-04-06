<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showDialog = true">添加用户</el-button>
        </div>
      </template>
      
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag>{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="editUser(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchUsers"
        @current-change="fetchUsers"
      />
    </el-card>

    <el-dialog v-model="showDialog" :title="editingUser ? '编辑用户' : '添加用户'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="医生" value="doctor" />
            <el-option label="护士" value="nurse" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editingUser" label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUserList, createUser, updateUser } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showDialog = ref(false)
const editingUser = ref(null)
const form = ref({
  username: '',
  real_name: '',
  email: '',
  role: 'nurse',
  password: ''
})

const getRoleText = (role) => {
  const texts = { admin: '管理员', doctor: '医生', nurse: '护士' }
  return texts[role] || role
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUserList({ page: page.value, page_size: pageSize.value })
    users.value = res?.items || []
    total.value = res?.total || 0
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  editingUser.value = user
  form.value = { ...user, password: '' }
  showDialog.value = true
}

const deleteUser = async (user) => {
  await ElMessageBox.confirm('确定要删除该用户吗？', '提示', { type: 'warning' })
  ElMessage.success('删除成功')
  fetchUsers()
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await updateUser(editingUser.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createUser(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
