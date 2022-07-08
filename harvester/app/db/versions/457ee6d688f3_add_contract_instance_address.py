"""Add contract instance address

Revision ID: 457ee6d688f3
Revises: 42310d504350
Create Date: 2021-03-18 15:55:25.523908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '457ee6d688f3'
down_revision = '42310d504350'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_event', sa.Column('contract_instance_address', sa.String(48), nullable=True))

def downgrade():
    op.drop_column('data_event', 'contract_instance_address')