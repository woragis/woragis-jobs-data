"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Company metrics table
    op.create_table(
        'company_metrics',
        sa.Column('company_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('total_applications', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time_days', sa.Integer(), nullable=True),
        sa.Column('avg_time_to_interview_days', sa.Integer(), nullable=True),
        sa.Column('avg_interview_count', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('avg_salary_min', sa.Integer(), nullable=True),
        sa.Column('avg_salary_max', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_company_metrics_updated', 'company_metrics', ['last_updated'])

    # User metrics table
    op.create_table(
        'user_metrics',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('total_applications', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time_days', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('avg_salary_range_min', sa.Integer(), nullable=True),
        sa.Column('avg_salary_range_max', sa.Integer(), nullable=True),
        sa.Column('preferred_company_sizes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('opportunity_score', sa.Integer(), nullable=False),
        sa.Column('tier', sa.String(length=10), nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),
        sa.Column('explanation', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_user_recommendations', 'recommendations', ['user_id', 'created_at'])
    op.create_index('idx_recommendations_expires', 'recommendations', ['expires_at'])

    # Recommendation history table
    op.create_table(
        'recommendation_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommended_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('user_action', sa.String(length=50), nullable=True),
        sa.Column('action_timestamp', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_history_user_action', 'recommendation_history', ['user_id', 'user_action'])

    # ML models table
    op.create_table(
        'ml_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_active', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('model_metadata', postgresql.JSON(), nullable=True),
    )
    op.create_index('idx_models_active', 'ml_models', ['model_name', 'is_active'])

    # Model predictions table
    op.create_table(
        'model_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prediction', postgresql.JSON(), nullable=False),
        sa.Column('actual_outcome', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_predictions_user', 'model_predictions', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_predictions_user', table_name='model_predictions')
    op.drop_table('model_predictions')
    op.drop_index('idx_models_active', table_name='ml_models')
    op.drop_table('ml_models')
    op.drop_index('idx_history_user_action', table_name='recommendation_history')
    op.drop_table('recommendation_history')
    op.drop_index('idx_recommendations_expires', table_name='recommendations')
    op.drop_index('idx_user_recommendations', table_name='recommendations')
    op.drop_table('recommendations')
    op.drop_table('user_metrics')
    op.drop_index('idx_company_metrics_updated', table_name='company_metrics')
    op.drop_table('company_metrics')

