"""update era length

Revision ID: 10d5bb76895a
Revises: 2ff452f5b2e9
Create Date: 2022-07-16 09:49:11.948619

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '10d5bb76895a'
down_revision = '2ff452f5b2e9'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('data_extrinsic', 'era',
                    existing_type=mysql.VARCHAR(length=4),
                    type_=mysql.VARCHAR(length=20),
                    existing_nullable=True)
    op.alter_column('data_reorg_extrinsic', 'era',
                    existing_type=mysql.VARCHAR(length=4),
                    type_=mysql.VARCHAR(length=20),
                    existing_nullable=True)


def downgrade():
    op.alter_column('data_extrinsic', 'era',
                    existing_type=mysql.VARCHAR(length=20),
                    type_=mysql.VARCHAR(length=4),
                    existing_nullable=True)
    op.alter_column('data_reorg_extrinsic', 'era',
                    existing_type=mysql.VARCHAR(length=20),
                    type_=mysql.VARCHAR(length=4),
                    existing_nullable=True)
