"""create account private table

Revision ID: 457ee6d688f4
Revises: 457ee6d688f3
Create Date: 2021-03-18 15:55:25.523908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '457ee6d688f4'
down_revision = '457ee6d688f3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('account_private',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account', sa.String(length=128), nullable=False),
        sa.Column('is_private', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account')
    )

def downgrade():
    op.drop_table('account_private')