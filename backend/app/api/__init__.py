from fastapi import APIRouter
from app.api.v1 import auth, users, elderly, health, alerts, interventions, reports, ml

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(elderly.router, prefix="/elderly", tags=["老人管理"])
api_router.include_router(health.router, prefix="/health", tags=["健康数据"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["预警管理"])
api_router.include_router(interventions.router, prefix="/interventions", tags=["干预管理"])
api_router.include_router(reports.router, prefix="/reports", tags=["统计报表"])
api_router.include_router(ml.router, prefix="/ml", tags=["深度学习"])
