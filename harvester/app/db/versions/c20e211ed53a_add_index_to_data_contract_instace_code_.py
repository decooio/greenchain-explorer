"""Add index to data_contract_instace.code_hash

Revision ID: c20e211ed53a
Revises: a57aa88dab75
Create Date: 2021-03-11 15:55:25.523908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c20e211ed53a'
down_revision = 'a57aa88dab75'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_data_contract_instance_code_hash'), 'data_contract_instance', ['code_hash'], unique=False)

def downgrade():
    op.drop_index('ix_data_contract_instance_code_hash', table_name='data_contract_instance')
