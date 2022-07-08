"""update runtime_storage default length

Revision ID: 0792ee77ad1c
Revises: 14ae152a128f
Create Date: 2021-02-13 09:32:03.828000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0792ee77ad1c'
down_revision = '14ae152a128f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('runtime_storage', 'default',
               existing_type=mysql.VARCHAR(length=512),
               nullable=True)


def downgrade():
    op.alter_column('runtime_storage', 'default',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
