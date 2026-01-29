"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create wrestlers table
    op.create_table(
        'wrestlers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('name_fa', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=False),
        sa.Column('weight_class', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('COMPETITION_READY', 'NORMAL', 'ATTENTION', name='wrestlerstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_wrestlers_team_id', 'wrestlers', ['team_id'])
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'COACH', 'ATHLETE', name='userrole'), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create overview_metrics table
    op.create_table(
        'overview_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('msi', sa.Float(), nullable=False),
        sa.Column('mes', sa.Float(), nullable=False),
        sa.Column('api', sa.Float(), nullable=False),
        sa.Column('vo2max', sa.Float(), nullable=False),
        sa.Column('frr', sa.Float(), nullable=False),
        sa.Column('acs', sa.Float(), nullable=False),
        sa.Column('bos', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_overview_metrics_wrestler_id', 'overview_metrics', ['wrestler_id'])
    
    # Create overview_series table
    op.create_table(
        'overview_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_overview_series_wrestler_id', 'overview_series', ['wrestler_id'])
    op.create_index('ix_overview_series_wrestler_recorded', 'overview_series', ['wrestler_id', 'recorded_at'])
    
    # Create body_composition_metrics table
    op.create_table(
        'body_composition_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('body_fat_percent', sa.Float(), nullable=False),
        sa.Column('muscle_mass', sa.Float(), nullable=False),
        sa.Column('bmr', sa.Float(), nullable=False),
        sa.Column('power_to_weight', sa.Float(), nullable=False),
        sa.Column('intracellular_water', sa.Float(), nullable=True),
        sa.Column('extracellular_water', sa.Float(), nullable=True),
        sa.Column('visceral_fat_level', sa.Float(), nullable=True),
        sa.Column('phase_angle', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_body_composition_metrics_wrestler_id', 'body_composition_metrics', ['wrestler_id'])
    
    # Create body_composition_series table
    op.create_table(
        'body_composition_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_body_composition_series_wrestler_id', 'body_composition_series', ['wrestler_id'])
    op.create_index('ix_body_composition_series_wrestler_recorded', 'body_composition_series', ['wrestler_id', 'recorded_at'])
    
    # Create bloodwork_metrics table
    op.create_table(
        'bloodwork_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('hemoglobin', sa.Float(), nullable=False),
        sa.Column('hematocrit', sa.Float(), nullable=False),
        sa.Column('testosterone', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('last_test_date', sa.Date(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bloodwork_metrics_wrestler_id', 'bloodwork_metrics', ['wrestler_id'])
    
    # Create bloodwork_series table
    op.create_table(
        'bloodwork_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('panel', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bloodwork_series_wrestler_id', 'bloodwork_series', ['wrestler_id'])
    op.create_index('ix_bloodwork_series_wrestler_recorded', 'bloodwork_series', ['wrestler_id', 'recorded_at'])
    
    # Create recovery_metrics table
    op.create_table(
        'recovery_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('sleep_quality', sa.Float(), nullable=False),
        sa.Column('hrv_score', sa.Float(), nullable=False),
        sa.Column('fatigue_level', sa.Float(), nullable=False),
        sa.Column('hydration_level', sa.Float(), nullable=False),
        sa.Column('readiness_score', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recovery_metrics_wrestler_id', 'recovery_metrics', ['wrestler_id'])
    
    # Create recovery_series table
    op.create_table(
        'recovery_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recovery_series_wrestler_id', 'recovery_series', ['wrestler_id'])
    op.create_index('ix_recovery_series_wrestler_recorded', 'recovery_series', ['wrestler_id', 'recorded_at'])
    
    # Create supplements_metrics table
    op.create_table(
        'supplements_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('adherence_rate', sa.Float(), nullable=False),
        sa.Column('monthly_progress', sa.String(length=20), nullable=False),
        sa.Column('performance_corr', sa.Float(), nullable=False),
        sa.Column('total_supplements', sa.Integer(), nullable=False),
        sa.Column('creatine_daily_grams', sa.Float(), nullable=False),
        sa.Column('protein_daily_grams', sa.Float(), nullable=False),
        sa.Column('hydration_liters', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supplements_metrics_wrestler_id', 'supplements_metrics', ['wrestler_id'])
    
    # Create supplements_series table
    op.create_table(
        'supplements_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supplements_series_wrestler_id', 'supplements_series', ['wrestler_id'])
    op.create_index('ix_supplements_series_wrestler_recorded', 'supplements_series', ['wrestler_id', 'recorded_at'])
    
    # Create performance_metrics table
    op.create_table(
        'performance_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('bench_max', sa.Float(), nullable=False),
        sa.Column('squat_max', sa.Float(), nullable=False),
        sa.Column('deadlift_max', sa.Float(), nullable=False),
        sa.Column('vo2max', sa.Float(), nullable=False),
        sa.Column('body_fat_percent', sa.Float(), nullable=False),
        sa.Column('performance_score', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_metrics_wrestler_id', 'performance_metrics', ['wrestler_id'])
    
    # Create performance_series table
    op.create_table(
        'performance_series',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_series_wrestler_id', 'performance_series', ['wrestler_id'])
    op.create_index('ix_performance_series_wrestler_recorded', 'performance_series', ['wrestler_id', 'recorded_at'])
    
    # Create training_programs table
    op.create_table(
        'training_programs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('focus', sa.String(length=255), nullable=True),
        sa.Column('readiness', sa.Integer(), nullable=True),
        sa.Column('session_rpe', sa.Integer(), nullable=True),
        sa.Column('bodyweight', sa.Float(), nullable=True),
        sa.Column('hydration', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('nutrition', sa.Text(), nullable=True),
        sa.Column('recovery', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_training_programs_wrestler_id', 'training_programs', ['wrestler_id'])
    
    # Create training_program_blocks table
    op.create_table(
        'training_program_blocks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('program_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps', sa.String(length=50), nullable=False),
        sa.Column('load', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['training_programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_training_program_blocks_program_id', 'training_program_blocks', ['program_id'])
    
    # Create training_program_ai_recommendations table
    op.create_table(
        'training_program_ai_recommendations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('program_id', sa.String(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['training_programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_training_program_ai_recommendations_program_id', 'training_program_ai_recommendations', ['program_id'])
    
    # Create ai_chart_insights table
    op.create_table(
        'ai_chart_insights',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('chart_id', sa.String(length=100), nullable=False),
        sa.Column('input_hash', sa.String(length=64), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('patterns_json', sa.Text(), nullable=True),
        sa.Column('recommendations_json', sa.Text(), nullable=True),
        sa.Column('warnings_json', sa.Text(), nullable=True),
        sa.Column('anomalies_json', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wrestler_id', 'chart_id', 'input_hash', name='uq_ai_insight_hash')
    )
    op.create_index('ix_ai_chart_insights_wrestler_id', 'ai_chart_insights', ['wrestler_id'])
    op.create_index('ix_ai_chart_insights_input_hash', 'ai_chart_insights', ['input_hash'])
    
    # Create section_scores table
    op.create_table(
        'section_scores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('wrestler_id', sa.String(), nullable=False),
        sa.Column('section_key', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('grade', sa.Enum('GOOD', 'WARNING', 'BAD', name='grade'), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wrestler_id'], ['wrestlers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_section_scores_wrestler_id', 'section_scores', ['wrestler_id'])
    op.create_index('ix_section_scores_wrestler_section_recorded', 'section_scores', ['wrestler_id', 'section_key', 'recorded_at'])
    
    # Create score_drivers table
    op.create_table(
        'score_drivers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('section_score_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('impact', sa.String(length=10), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['section_score_id'], ['section_scores.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_score_drivers_section_score_id', 'score_drivers', ['section_score_id'])
    
    # Create token_blacklist table
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token_jti', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti')
    )
    op.create_index('ix_token_blacklist_token_jti', 'token_blacklist', ['token_jti'])


def downgrade() -> None:
    op.drop_table('token_blacklist')
    op.drop_table('score_drivers')
    op.drop_table('section_scores')
    op.drop_table('ai_chart_insights')
    op.drop_table('training_program_ai_recommendations')
    op.drop_table('training_program_blocks')
    op.drop_table('training_programs')
    op.drop_table('performance_series')
    op.drop_table('performance_metrics')
    op.drop_table('supplements_series')
    op.drop_table('supplements_metrics')
    op.drop_table('recovery_series')
    op.drop_table('recovery_metrics')
    op.drop_table('bloodwork_series')
    op.drop_table('bloodwork_metrics')
    op.drop_table('body_composition_series')
    op.drop_table('body_composition_metrics')
    op.drop_table('overview_series')
    op.drop_table('overview_metrics')
    op.drop_table('users')
    op.drop_table('wrestlers')
    op.drop_table('teams')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS wrestlerstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS grade")
