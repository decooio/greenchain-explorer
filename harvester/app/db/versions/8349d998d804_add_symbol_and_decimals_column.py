"""add symbol and decimals column

Revision ID: 8349d998d804
Revises: c20e211ed53a
Create Date: 2021-03-15 08:31:11.807393

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8349d998d804'
down_revision = 'c20e211ed53a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_contract_instance', sa.Column('decimals', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('data_contract_instance', 'decimals')
