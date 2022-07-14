"""update runtime_event_attribute type

Revision ID: 7b05c4752a6c
Revises: 457ee6d688f4
Create Date: 2022-07-14 16:13:37.463550

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7b05c4752a6c'
down_revision = '457ee6d688f4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('runtime_event_attribute', 'type',
                    existing_type=mysql.VARCHAR(length=255),
                    type_=mysql.JSON,
                    existing_nullable=True)


def downgrade():
    op.alter_column('runtime_event_attribute', 'type',
                    existing_type=mysql.JSON,
                    type_=mysql.VARCHAR(length=255),
                    existing_nullable=True)
