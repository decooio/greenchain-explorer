"""update data_event type length

Revision ID: 14ae152a128f
Revises: 2e13a031e4d4
Create Date: 2021-02-12 23:17:15.366218

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '14ae152a128f'
down_revision = '2e13a031e4d4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('data_event', 'type',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)


def downgrade():
    op.alter_column('data_event', 'type',
               existing_type=mysql.VARCHAR(length=4),
               nullable=True)
