import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import ElderlyInfo, Alert, AlertRule, HealthMetric, Device

async def add_health_data():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ElderlyInfo).limit(15))
        elderly_list = result.scalars().all()
        
        result = await db.execute(select(AlertRule))
        rules = result.scalars().all()
        
        result = await db.execute(select(HealthMetric))
        metrics = result.scalars().all()
        
        if not elderly_list:
            print("没有老人数据")
            return
        
        alerts_to_add = []
        
        alert_templates = [
            {"title": "心率异常预警", "content": "心率超过正常范围，请及时关注", "alert_level": "high", "alert_type": "heart_rate"},
            {"title": "血压异常预警", "content": "血压偏高，建议测量复查", "alert_level": "critical", "alert_type": "blood_pressure"},
            {"title": "体温异常预警", "content": "体温偏高，可能有发热症状", "alert_level": "medium", "alert_type": "temperature"},
            {"title": "血氧异常预警", "content": "血氧饱和度偏低，请关注", "alert_level": "critical", "alert_type": "spo2"},
            {"title": "血糖异常预警", "content": "血糖偏高，请注意饮食控制", "alert_level": "high", "alert_type": "blood_glucose"},
            {"title": "活动异常预警", "content": "今日活动量较少，建议适当运动", "alert_level": "low", "alert_type": "activity"},
            {"title": "睡眠异常预警", "content": "睡眠时长不足，请关注休息", "alert_level": "medium", "alert_type": "sleep"},
        ]
        
        for elderly in elderly_list:
            num_alerts = random.randint(1, 3)
            selected_alerts = random.sample(alert_templates, num_alerts)
            
            for alert_data in selected_alerts:
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
                
                alert = Alert(
                    elderly_id=elderly.id,
                    rule_id=random.choice(rules).id if rules else None,
                    alert_level=alert_data["alert_level"],
                    alert_type=alert_data["alert_type"],
                    title=f"{elderly.name} - {alert_data['title']}",
                    content=alert_data["content"],
                    metric_value=random.uniform(60, 150),
                    status=random.choice(["pending", "pending", "pending", "resolved", "processing"]),
                    created_at=created_at,
                    updated_at=created_at,
                )
                alerts_to_add.append(alert)
        
        for alert in alerts_to_add:
            db.add(alert)
        
        await db.commit()
        print(f"已添加 {len(alerts_to_add)} 条预警记录")
        
        result = await db.execute(select(Alert))
        total = len(result.scalars().all())
        print(f"数据库中共有 {total} 条预警记录")

async def add_devices():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ElderlyInfo).limit(10))
        elderly_list = result.scalars().all()
        
        device_types = [
            {"device_type": "heart_rate_monitor", "name": "心率监测仪"},
            {"device_type": "blood_pressure_monitor", "name": "血压计"},
            {"device_type": "thermometer", "name": "体温计"},
            {"device_type": "oximeter", "name": "血氧仪"},
            {"device_type": "glucose_meter", "name": "血糖仪"},
            {"device_type": "smart_watch", "name": "智能手环"},
        ]
        
        devices_added = 0
        for i, elderly in enumerate(elderly_list):
            for j, device_type in enumerate(device_types[:3]):
                device = Device(
                    device_code=f"DEV{str(i).zfill(3)}{str(j).zfill(2)}",
                    device_name=device_type["name"],
                    device_type=device_type["device_type"],
                    elderly_id=elderly.id,
                    status="active",
                    last_data_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
                )
                db.add(device)
                devices_added += 1
        
        await db.commit()
        print(f"已添加 {devices_added} 台设备")

async def main():
    print("正在添加预警数据...")
    await add_health_data()
    print("\n正在添加设备数据...")
    await add_devices()
    print("\n数据添加完成！")

if __name__ == "__main__":
    asyncio.run(main())
