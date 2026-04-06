import asyncio
from sqlalchemy import select
from app.db import engine, AsyncSessionLocal
from app.models import Base, HealthMetric, AlertRule, User, Institution, ElderlyInfo
from app.core.security import get_password_hash
from datetime import date, timedelta
import random


async def init_health_metrics(db):
    metrics = [
        {"name": "心率", "code": "heart_rate", "unit": "次/分", "normal_min": 60, "normal_max": 100, "warning_min": 50, "warning_max": 120, "category": "vital_signs"},
        {"name": "收缩压", "code": "systolic_bp", "unit": "mmHg", "normal_min": 90, "normal_max": 140, "warning_min": 80, "warning_max": 180, "category": "vital_signs"},
        {"name": "舒张压", "code": "diastolic_bp", "unit": "mmHg", "normal_min": 60, "normal_max": 90, "warning_min": 50, "warning_max": 110, "category": "vital_signs"},
        {"name": "体温", "code": "temperature", "unit": "℃", "normal_min": 36.0, "normal_max": 37.5, "warning_min": 35.0, "warning_max": 39.0, "category": "vital_signs"},
        {"name": "血氧饱和度", "code": "spo2", "unit": "%", "normal_min": 95, "normal_max": 100, "warning_min": 90, "warning_max": 100, "category": "vital_signs"},
        {"name": "血糖(空腹)", "code": "blood_glucose_fasting", "unit": "mmol/L", "normal_min": 3.9, "normal_max": 6.1, "warning_min": 2.8, "warning_max": 10.0, "category": "vital_signs"},
        {"name": "血糖(餐后)", "code": "blood_glucose_postprandial", "unit": "mmol/L", "normal_min": 3.9, "normal_max": 7.8, "warning_min": 2.8, "warning_max": 15.0, "category": "vital_signs"},
        {"name": "步数", "code": "steps", "unit": "步", "normal_min": 1000, "normal_max": 10000, "warning_min": 0, "warning_max": 20000, "category": "activity"},
        {"name": "睡眠时长", "code": "sleep_duration", "unit": "小时", "normal_min": 6, "normal_max": 9, "warning_min": 4, "warning_max": 12, "category": "activity"},
        {"name": "室内温度", "code": "room_temperature", "unit": "℃", "normal_min": 18.0, "normal_max": 26.0, "warning_min": 10.0, "warning_max": 35.0, "category": "environment"},
        {"name": "室内湿度", "code": "room_humidity", "unit": "%", "normal_min": 40.0, "normal_max": 70.0, "warning_min": 20.0, "warning_max": 90.0, "category": "environment"},
    ]
    
    for metric_data in metrics:
        result = await db.execute(select(HealthMetric).where(HealthMetric.code == metric_data["code"]))
        if not result.scalar_one_or_none():
            metric = HealthMetric(**metric_data)
            db.add(metric)
    
    await db.commit()


async def init_alert_rules(db):
    rules = [
        {"name": "心率过快预警", "metric_code": "heart_rate", "condition_type": "gt", "threshold_value": 120, "alert_level": "high", "description": "心率超过120次/分"},
        {"name": "心率过慢预警", "metric_code": "heart_rate", "condition_type": "lt", "threshold_value": 50, "alert_level": "high", "description": "心率低于50次/分"},
        {"name": "高血压预警", "metric_code": "systolic_bp", "condition_type": "gt", "threshold_value": 180, "alert_level": "critical", "description": "收缩压超过180mmHg"},
        {"name": "低血压预警", "metric_code": "systolic_bp", "condition_type": "lt", "threshold_value": 80, "alert_level": "high", "description": "收缩压低于80mmHg"},
        {"name": "高热预警", "metric_code": "temperature", "condition_type": "gt", "threshold_value": 39, "alert_level": "critical", "description": "体温超过39℃"},
        {"name": "低血氧预警", "metric_code": "spo2", "condition_type": "lt", "threshold_value": 90, "alert_level": "critical", "description": "血氧饱和度低于90%"},
        {"name": "高血糖预警", "metric_code": "blood_glucose_fasting", "condition_type": "gt", "threshold_value": 10, "alert_level": "high", "description": "空腹血糖超过10mmol/L"},
        {"name": "低血糖预警", "metric_code": "blood_glucose_fasting", "condition_type": "lt", "threshold_value": 3.9, "alert_level": "critical", "description": "空腹血糖低于3.9mmol/L"},
    ]
    
    for rule_data in rules:
        result = await db.execute(select(AlertRule).where(AlertRule.name == rule_data["name"]))
        if not result.scalar_one_or_none():
            rule = AlertRule(**rule_data)
            db.add(rule)
    
    await db.commit()


async def init_admin_user(db):
    result = await db.execute(select(User).where(User.username == "admin"))
    if not result.scalar_one_or_none():
        institution = Institution(
            name="阳光养老院",
            address="北京市朝阳区幸福路88号",
            contact_phone="010-12345678",
            contact_email="contact@sunshine-elderly.com",
            capacity=200,
        )
        db.add(institution)
        await db.commit()
        await db.refresh(institution)
        
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@example.com",
            real_name="系统管理员",
            role="admin",
            institution_id=institution.id,
        )
        db.add(admin)
        
        doctor = User(
            username="doctor",
            password_hash=get_password_hash("doctor123"),
            email="doctor@example.com",
            real_name="王医生",
            role="doctor",
            institution_id=institution.id,
        )
        db.add(doctor)
        
        nurse = User(
            username="nurse",
            password_hash=get_password_hash("nurse123"),
            email="nurse@example.com",
            real_name="李护士",
            role="nurse",
            institution_id=institution.id,
        )
        db.add(nurse)
        
        await db.commit()
        return institution.id
    else:
        result = await db.execute(select(Institution).limit(1))
        institution = result.scalar_one_or_none()
        return institution.id if institution else None


async def init_elderly_data(db, institution_id):
    elderly_list = [
        {"name": "张大爷", "gender": "男", "birth_date": date(1945, 3, 15), "id_card": "110101194503150011", "blood_type": "A", "height": 172, "weight": 75, "room_number": "101", "bed_number": "1", "allergies": "青霉素", "chronic_diseases": "高血压、糖尿病", "medications": "降压药、降糖药"},
        {"name": "李奶奶", "gender": "女", "birth_date": date(1948, 6, 22), "id_card": "110101194806220022", "blood_type": "B", "height": 158, "weight": 55, "room_number": "101", "bed_number": "2", "allergies": "无", "chronic_diseases": "关节炎", "medications": "止痛药"},
        {"name": "王大爷", "gender": "男", "birth_date": date(1942, 1, 8), "id_card": "110101194201080033", "blood_type": "O", "height": 175, "weight": 80, "room_number": "102", "bed_number": "1", "allergies": "磺胺类", "chronic_diseases": "冠心病", "medications": "心脏药物"},
        {"name": "赵奶奶", "gender": "女", "birth_date": date(1950, 9, 30), "id_card": "110101195009300044", "blood_type": "AB", "height": 160, "weight": 58, "room_number": "102", "bed_number": "2", "allergies": "无", "chronic_diseases": "无", "medications": "无"},
        {"name": "刘大爷", "gender": "男", "birth_date": date(1946, 11, 12), "id_card": "110101194611120055", "blood_type": "A", "height": 168, "weight": 70, "room_number": "103", "bed_number": "1", "allergies": "无", "chronic_diseases": "高血压", "medications": "降压药"},
        {"name": "陈奶奶", "gender": "女", "birth_date": date(1952, 4, 5), "id_card": "110101195204050066", "blood_type": "B", "height": 155, "weight": 52, "room_number": "103", "bed_number": "2", "allergies": "海鲜", "chronic_diseases": "糖尿病", "medications": "胰岛素"},
        {"name": "孙大爷", "gender": "男", "birth_date": date(1944, 7, 18), "id_card": "110101194407180077", "blood_type": "O", "height": 170, "weight": 72, "room_number": "104", "bed_number": "1", "allergies": "无", "chronic_diseases": "慢性支气管炎", "medications": "止咳药"},
        {"name": "周奶奶", "gender": "女", "birth_date": date(1949, 12, 25), "id_card": "110101194912250088", "blood_type": "A", "height": 162, "weight": 60, "room_number": "104", "bed_number": "2", "allergies": "花粉", "chronic_diseases": "骨质疏松", "medications": "钙片"},
        {"name": "吴大爷", "gender": "男", "birth_date": date(1943, 2, 28), "id_card": "110101194302280099", "blood_type": "AB", "height": 176, "weight": 78, "room_number": "105", "bed_number": "1", "allergies": "无", "chronic_diseases": "高血压、高血脂", "medications": "降压药、降脂药"},
        {"name": "郑奶奶", "gender": "女", "birth_date": date(1951, 8, 10), "id_card": "110101195108100100", "blood_type": "B", "height": 156, "weight": 50, "room_number": "105", "bed_number": "2", "allergies": "无", "chronic_diseases": "轻度认知障碍", "medications": "改善认知药物"},
        {"name": "冯大爷", "gender": "男", "birth_date": date(1947, 5, 20), "id_card": "110101194705200111", "blood_type": "A", "height": 169, "weight": 68, "room_number": "106", "bed_number": "1", "allergies": "青霉素", "chronic_diseases": "前列腺增生", "medications": "前列腺药物"},
        {"name": "卫奶奶", "gender": "女", "birth_date": date(1953, 10, 3), "id_card": "110101195310030122", "blood_type": "O", "height": 158, "weight": 54, "room_number": "106", "bed_number": "2", "allergies": "无", "chronic_diseases": "失眠症", "medications": "安眠药"},
        {"name": "蒋大爷", "gender": "男", "birth_date": date(1941, 6, 15), "id_card": "110101194106150133", "blood_type": "B", "height": 173, "weight": 76, "room_number": "107", "bed_number": "1", "allergies": "无", "chronic_diseases": "帕金森病", "medications": "帕金森药物"},
        {"name": "沈奶奶", "gender": "女", "birth_date": date(1954, 3, 8), "id_card": "110101195403080144", "blood_type": "AB", "height": 160, "weight": 56, "room_number": "107", "bed_number": "2", "allergies": "碘酒", "chronic_diseases": "甲状腺功能减退", "medications": "甲状腺素"},
        {"name": "韩大爷", "gender": "男", "birth_date": date(1940, 9, 22), "id_card": "110101194009220155", "blood_type": "O", "height": 171, "weight": 74, "room_number": "108", "bed_number": "1", "allergies": "无", "chronic_diseases": "糖尿病、高血压", "medications": "胰岛素、降压药"},
    ]
    
    result = await db.execute(select(User).where(User.role == "nurse").limit(1))
    nurse = result.scalar_one_or_none()
    nurse_id = nurse.id if nurse else None
    
    for elderly_data in elderly_list:
        result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id_card == elderly_data["id_card"]))
        if not result.scalar_one_or_none():
            elderly = ElderlyInfo(
                **elderly_data,
                institution_id=institution_id,
                nurse_id=nurse_id,
                admission_date=date.today() - timedelta(days=random.randint(30, 365)),
                status="active"
            )
            db.add(elderly)
    
    await db.commit()


async def main():
    print("正在初始化数据库...")
    
    print("创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成")
    
    async with AsyncSessionLocal() as db:
        await init_health_metrics(db)
        print("健康指标初始化完成")
        
        await init_alert_rules(db)
        print("预警规则初始化完成")
        
        institution_id = await init_admin_user(db)
        print("用户账户初始化完成")
        
        if institution_id:
            await init_elderly_data(db, institution_id)
            print("老人数据初始化完成")
    
    print("\n初始化完成！")
    print("默认管理员账号: admin / admin123")
    print("医生账号: doctor / doctor123")
    print("护士账号: nurse / nurse123")


if __name__ == "__main__":
    asyncio.run(main())
