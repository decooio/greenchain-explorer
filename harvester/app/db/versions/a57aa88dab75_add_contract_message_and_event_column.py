"""add contract message and event column

Revision ID: a57aa88dab75
Revises: 5e75cbb22b51
Create Date: 2021-03-10 22:28:57.897207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a57aa88dab75'
down_revision = '5e75cbb22b51'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_extrinsic', sa.Column('contract_message', sa.JSON(), nullable=True))
    op.add_column('data_event', sa.Column('contract_event', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('data_extrinsic', "contract_message")
    op.drop_column('data_event', "contract_event")
