from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'institutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('address', sa.String(255)),
        sa.Column('contact_phone', sa.String(20)),
        sa.Column('contact_email', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('capacity', sa.Integer),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email', sa.String(100), unique=True),
        sa.Column('phone', sa.String(20)),
        sa.Column('real_name', sa.String(50)),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('institutions.id')),
        sa.Column('last_login_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    op.create_table(
        'elderly_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('gender', sa.String(10), nullable=False),
        sa.Column('birth_date', sa.Date, nullable=False),
        sa.Column('id_card', sa.String(18), unique=True),
        sa.Column('blood_type', sa.String(5)),
        sa.Column('height', sa.Numeric(5, 2)),
        sa.Column('weight', sa.Numeric(5, 2)),
        sa.Column('allergies', postgresql.JSONB),
        sa.Column('chronic_diseases', postgresql.JSONB),
        sa.Column('medications', postgresql.JSONB),
        sa.Column('emergency_contact', postgresql.JSONB),
        sa.Column('room_number', sa.String(20)),
        sa.Column('bed_number', sa.String(20)),
        sa.Column('admission_date', sa.Date),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('institutions.id')),
        sa.Column('nurse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'health_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('code', sa.String(30), unique=True, nullable=False),
        sa.Column('unit', sa.String(20)),
        sa.Column('normal_min', sa.Numeric(10, 2)),
        sa.Column('normal_max', sa.Numeric(10, 2)),
        sa.Column('warning_min', sa.Numeric(10, 2)),
        sa.Column('warning_max', sa.Numeric(10, 2)),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(50)),
    )
    
    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('device_code', sa.String(50), unique=True, nullable=False),
        sa.Column('device_name', sa.String(100), nullable=False),
        sa.Column('device_type', sa.String(50), nullable=False),
        sa.Column('manufacturer', sa.String(100)),
        sa.Column('model', sa.String(50)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('elderly_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elderly_info.id')),
        sa.Column('last_data_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'alert_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('metric_code', sa.String(30), nullable=False),
        sa.Column('condition_type', sa.String(20), nullable=False),
        sa.Column('threshold_value', sa.Numeric(10, 2)),
        sa.Column('duration_minutes', sa.Integer),
        sa.Column('alert_level', sa.String(20), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('elderly_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elderly_info.id'), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alert_rules.id')),
        sa.Column('alert_level', sa.String(20), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metric_value', sa.Numeric(10, 2)),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('handler_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('handle_time', sa.DateTime),
        sa.Column('handle_result', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'intervention_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('alert_type', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('steps', postgresql.JSONB),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('is_template', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'intervention_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('elderly_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elderly_info.id'), nullable=False),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id')),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intervention_plans.id')),
        sa.Column('executor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime),
        sa.Column('status', sa.String(20), server_default='ongoing'),
        sa.Column('content', sa.Text),
        sa.Column('result', sa.Text),
        sa.Column('effectiveness', sa.String(20)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'health_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('elderly_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elderly_info.id'), nullable=False),
        sa.Column('record_date', sa.Date, nullable=False),
        sa.Column('health_status', sa.Text),
        sa.Column('nursing_level', sa.String(20)),
        sa.Column('special_care', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table(
        'operation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('detail', postgresql.JSONB),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('operation_logs')
    op.drop_table('health_records')
    op.drop_table('intervention_records')
    op.drop_table('intervention_plans')
    op.drop_table('alerts')
    op.drop_table('alert_rules')
    op.drop_table('devices')
    op.drop_table('health_metrics')
    op.drop_table('elderly_info')
    op.drop_table('users')
    op.drop_table('institutions')
