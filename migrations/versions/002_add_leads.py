"""Add Lead model for tracking unregistered users."""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Create the leads table."""
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('first_message', sa.Text(), nullable=True),
        sa.Column('last_message', sa.Text(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('converted_to_student', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('student_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_phone_number'), 'leads', ['phone_number'], unique=True)
    op.create_index(op.f('ix_leads_created_at'), 'leads', ['created_at'])
    op.create_index(op.f('ix_leads_updated_at'), 'leads', ['updated_at'])
    op.create_index(op.f('ix_leads_student_id'), 'leads', ['student_id'])


def downgrade():
    """Drop the leads table."""
    op.drop_index(op.f('ix_leads_student_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_updated_at'), table_name='leads')
    op.drop_index(op.f('ix_leads_created_at'), table_name='leads')
    op.drop_index(op.f('ix_leads_phone_number'), table_name='leads')
    op.drop_table('leads')
