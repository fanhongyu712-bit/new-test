# 养老机构健康监测与风险预警系统

基于深度学习的养老机构老人健康监测与风险预警系统

## 环境要求

- Python 3.9+
- Node.js 18+

## 快速启动（推荐）

### 方式一：一键启动

双击运行 `start_all.bat` 文件，将自动启动后端和前端服务。

### 方式二：分别启动

1. **启动后端**：双击 `start_backend.bat`
2. **启动前端**：双击 `start_frontend.bat`

### 方式三：命令行启动

#### 后端服务

```bash
cd backend

# 创建虚拟环境（首次运行）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 初始化数据库（首次运行）
python -c "from app.init_data import main; import asyncio; asyncio.run(main())"

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 前端服务

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动服务
npm run dev
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端API文档 | http://localhost:8000/api/v1/docs |
| 后端根路径 | http://localhost:8000 |

## 默认账号

- **用户名**: admin
- **密码**: admin123

## 系统功能

### 核心功能
- ✅ 用户认证与权限管理
- ✅ 老人信息管理
- ✅ 健康数据监测与可视化
- ✅ 多级别风险预警
- ✅ 干预记录与跟踪
- ✅ 统计报表

### 技术特点
- 前后端分离架构
- SQLite数据库（无需额外安装）
- 基于深度学习的风险评估
- 实时数据可视化
- 响应式前端界面

## 项目结构

```
traeTest/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库连接
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── ml/             # 机器学习模块
│   ├── requirements.txt    # Python依赖
│   └── main.py             # 入口文件
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API封装
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   └── views/          # 页面组件
│   └── package.json        # Node依赖
├── docs/                   # 设计文档
├── start_backend.bat       # 后端启动脚本
├── start_frontend.bat      # 前端启动脚本
└── start_all.bat           # 一键启动脚本
```

## 常见问题

### 1. Python未安装或版本过低
- 下载安装 Python 3.9+ : https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### 2. Node.js未安装
- 下载安装 Node.js 18+ : https://nodejs.org/

### 3. 端口被占用
- 后端默认端口: 8000
- 前端默认端口: 5173
- 如需修改，请编辑相应配置文件

### 4. 依赖安装失败
- 后端: 尝试使用国内镜像
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- 前端: 尝试使用国内镜像
  ```bash
  npm install --registry=https://registry.npmmirror.com
  ```

## 开发说明

### API文档
启动后端后访问 http://localhost:8000/api/v1/docs 查看完整的API文档

### 数据库
系统使用SQLite数据库，数据文件位于 `backend/elderly_health.db`

### 模型训练
如需训练深度学习模型，请参考 `backend/train_models.py`

## 技术栈

### 后端
- FastAPI - 高性能Web框架
- SQLAlchemy - ORM
- SQLite - 数据库
- Pydantic - 数据验证

### 前端
- Vue.js 3 - 前端框架
- Element Plus - UI组件库
- ECharts - 图表库
- Pinia - 状态管理
- Axios - HTTP客户端

## 许可证

本项目仅供学习和研究使用。
