"""Add support_tickets and support_messages tables

Revision ID: 002_add_support_tables
Revises: 
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002_add_support_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create support_tickets table
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('sender_name', sa.String(255), nullable=True),
        sa.Column('issue_description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', name='ticketstatus'), nullable=False, server_default='OPEN'),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='ticketpriority'), nullable=False, server_default='MEDIUM'),
        sa.Column('assigned_admin_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    # Create indexes for support_tickets
    op.create_index('idx_phone_number_status', 'support_tickets', ['phone_number', 'status'])
    op.create_index('idx_status', 'support_tickets', ['status'])
    op.create_index('idx_assigned_admin', 'support_tickets', ['assigned_admin_id'])
    op.create_index('idx_student_id', 'support_tickets', ['student_id'])
    
    # Create support_messages table
    op.create_table(
        'support_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.String(10), nullable=False),
        sa.Column('sender_name', sa.String(255), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    # Create index for support_messages
    op.create_index('idx_ticket_id_created', 'support_messages', ['ticket_id', 'created_at'])


def downgrade() -> None:
    # Drop support_messages table
    op.drop_index('idx_ticket_id_created', table_name='support_messages')
    op.drop_table('support_messages')
    
    # Drop support_tickets table
    op.drop_index('idx_student_id', table_name='support_tickets')
    op.drop_index('idx_assigned_admin', table_name='support_tickets')
    op.drop_index('idx_status', table_name='support_tickets')
    op.drop_index('idx_phone_number_status', table_name='support_tickets')
    op.drop_table('support_tickets')
