"""
Migration: Add Tutor Support Tables

This migration adds:
- Tutor model/table
- TutorAssignment model/table  
- TutorSolution model/table
- Updates Homework table with tutor assignment fields
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    """Create new tables and columns."""
    
    # Create tutors table
    op.create_table(
        'tutors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone_number', sa.String(20), unique=True, nullable=False),
        sa.Column('subjects', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('bio', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('idx_email', 'tutors', ['email'])
    op.create_index('idx_phone', 'tutors', ['phone_number'])
    op.create_index('idx_is_active', 'tutors', ['is_active'])
    
    # Create tutor_assignments table
    op.create_table(
        'tutor_assignments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('homework_id', sa.Integer, sa.ForeignKey('homeworks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tutor_id', sa.Integer, sa.ForeignKey('tutors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'), nullable=False, default='PENDING'),
        sa.Column('assigned_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('idx_homework_id', 'tutor_assignments', ['homework_id'])
    op.create_index('idx_tutor_id', 'tutor_assignments', ['tutor_id'])
    op.create_index('idx_status', 'tutor_assignments', ['status'])
    op.create_index('idx_assigned_at', 'tutor_assignments', ['assigned_at'])
    
    # Create tutor_solutions table
    op.create_table(
        'tutor_solutions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('assignment_id', sa.Integer, sa.ForeignKey('tutor_assignments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tutor_id', sa.Integer, sa.ForeignKey('tutors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('solution_text', sa.Text, nullable=True),
        sa.Column('solution_file_path', sa.String(500), nullable=True),
        sa.Column('is_walkthrough_video', sa.Boolean, default=False, nullable=False),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('submitted_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('idx_assignment_id', 'tutor_solutions', ['assignment_id'])
    op.create_index('idx_tutor_id_solutions', 'tutor_solutions', ['tutor_id'])
    
    # Alter homeworks table to add tutor fields
    op.add_column('homeworks', sa.Column('status', sa.Enum('PENDING', 'PAID', 'ASSIGNED', 'IN_PROGRESS', 'SOLVED', 'CANCELLED'), default='PENDING', nullable=False))
    op.add_column('homeworks', sa.Column('assigned_tutor_id', sa.Integer, sa.ForeignKey('tutors.id', ondelete='SET NULL'), nullable=True))
    op.create_index('idx_status', 'homeworks', ['status'])
    op.create_index('idx_assigned_tutor', 'homeworks', ['assigned_tutor_id'])


def downgrade():
    """Rollback migration."""
    
    # Drop indexes from homeworks
    op.drop_index('idx_status', table_name='homeworks')
    op.drop_index('idx_assigned_tutor', table_name='homeworks')
    
    # Drop columns from homeworks
    op.drop_column('homeworks', 'assigned_tutor_id')
    op.drop_column('homeworks', 'status')
    
    # Drop tutor_solutions table
    op.drop_table('tutor_solutions')
    
    # Drop tutor_assignments table
    op.drop_table('tutor_assignments')
    
    # Drop tutors table
    op.drop_table('tutors')
