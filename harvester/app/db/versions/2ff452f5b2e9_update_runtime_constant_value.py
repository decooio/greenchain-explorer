"""update runtime_constant value

Revision ID: 2ff452f5b2e9
Revises: 7b05c4752a6c
Create Date: 2022-07-14 16:20:18.254689

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '2ff452f5b2e9'
down_revision = '7b05c4752a6c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('runtime_constant', 'value',
                    existing_type=mysql.VARCHAR(length=255),
                    type_=mysql.LONGTEXT(),
                    existing_nullable=True)


def downgrade():
    op.alter_column('runtime_constant', 'value',
                    existing_type=mysql.LONGTEXT(),
                    type_=mysql.VARCHAR(length=255),
                    existing_nullable=True)
