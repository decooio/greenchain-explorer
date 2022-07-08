"""add the table of contract instance

Revision ID: c8af8b4a3ecf
Revises: 0792ee77ad1c
Create Date: 2021-03-01 09:35:33.033520

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c8af8b4a3ecf'
down_revision = '0792ee77ad1c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('data_contract_instance',
        sa.Column('address', sa.String(length=48), nullable=False),
        sa.Column('code_hash', sa.String(length=64), nullable=True),
        sa.Column('owner', sa.String(length=48), nullable=True),
        sa.Column('name', sa.String(length=24), nullable=True),
        sa.Column('symbol', sa.String(length=24), nullable=True),
        sa.Column('created_at_block', sa.Integer(), nullable=False),
        sa.Column('created_at_extrinsic', sa.Integer(), nullable=True),
        sa.Column('created_at_event', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('address')
    )

def downgrade():
    op.drop_table('data_contract_instance')
    
    # ### end Alembic commands ###