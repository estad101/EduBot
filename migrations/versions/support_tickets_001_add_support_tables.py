"""Add support tickets and messages tables

Revision ID: support_tickets_001
Revises: 
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'support_tickets_001'
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
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', name='ticketstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='ticketpriority'), nullable=False),
        sa.Column('assigned_admin_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
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
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_id_created', 'support_messages', ['ticket_id', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_ticket_id_created', table_name='support_messages')
    op.drop_index('idx_student_id', table_name='support_tickets')
    op.drop_index('idx_assigned_admin', table_name='support_tickets')
    op.drop_index('idx_status', table_name='support_tickets')
    op.drop_index('idx_phone_number_status', table_name='support_tickets')
    
    # Drop tables
    op.drop_table('support_messages')
    op.drop_table('support_tickets')
