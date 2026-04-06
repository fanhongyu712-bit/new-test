from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models import AlertRule, Alert, ElderlyInfo
from app.schemas import AlertRuleCreate, AlertRuleResponse, AlertCreate, AlertUpdate, AlertResponse, RiskAssessmentResponse
from app.schemas.common import ResponseBase, PaginatedResponse

router = APIRouter()


@router.get("/rules", response_model=ResponseBase[list[AlertRuleResponse]])
async def list_alert_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule))
    rules = result.scalars().all()
    
    return ResponseBase(data=[AlertRuleResponse.model_validate(r) for r in rules])


@router.put("/rules/{rule_id}", response_model=ResponseBase[AlertRuleResponse])
async def update_alert_rule(rule_id: str, is_active: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        return ResponseBase(code=404, message="预警规则不存在")
    
    rule.is_active = is_active
    await db.commit()
    await db.refresh(rule)
    
    return ResponseBase(data=AlertRuleResponse.model_validate(rule), message="更新成功")


@router.get("/risk-assessment/{elderly_id}", response_model=ResponseBase[RiskAssessmentResponse])
async def get_risk_assessment(elderly_id: str, db: AsyncSession = Depends(get_db)):
    import random
    
    risk_factors = [
        {"type": "metric_high", "metric": "心率", "value": 125, "threshold": 120},
        {"type": "chronic_disease", "name": "高血压"},
    ]
    
    recommendations = [
        "建议立即进行健康检查",
        "通知责任医生进行评估",
        "增加巡视频率",
    ]
    
    return ResponseBase(
        data=RiskAssessmentResponse(
            elderly_id=elderly_id,
            risk_level="high",
            risk_score=75.5,
            risk_factors=risk_factors,
            recommendations=recommendations,
            assessed_at=datetime.utcnow(),
        )
    )


@router.get("", response_model=ResponseBase[PaginatedResponse[AlertResponse]])
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    alert_level: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert).options(selectinload(Alert.elderly))
    count_query = select(func.count(Alert.id))
    
    if alert_level:
        query = query.where(Alert.alert_level == alert_level)
        count_query = count_query.where(Alert.alert_level == alert_level)
    
    if status:
        query = query.where(Alert.status == status)
        count_query = count_query.where(Alert.status == status)
    
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    items = []
    for alert in alerts:
        alert_dict = {
            "id": alert.id,
            "elderly_id": alert.elderly_id,
            "rule_id": alert.rule_id,
            "alert_level": alert.alert_level,
            "alert_type": alert.alert_type,
            "title": alert.title,
            "content": alert.content,
            "metric_value": float(alert.metric_value) if alert.metric_value else None,
            "status": alert.status,
            "handler_id": alert.handler_id,
            "handle_time": alert.handle_time,
            "handle_result": alert.handle_result,
            "created_at": alert.created_at,
            "elderly_name": alert.elderly.name if alert.elderly else None
        }
        items.append(AlertResponse(**alert_dict))
    
    return ResponseBase(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total else 0,
        )
    )


@router.put("/{alert_id}/handle", response_model=ResponseBase[AlertResponse])
async def handle_alert(alert_id: str, handle_result: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        return ResponseBase(code=404, message="预警信息不存在")
    
    alert.status = "resolved"
    alert.handle_time = datetime.utcnow()
    alert.handle_result = handle_result
    
    await db.commit()
    await db.refresh(alert)
    
    return ResponseBase(data=AlertResponse.model_validate(alert), message="处理成功")
