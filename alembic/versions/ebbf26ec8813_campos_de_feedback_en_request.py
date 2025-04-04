"""Campos de feedback en request

Revision ID: ebbf26ec8813
Revises: c9ceec07b923
Create Date: 2025-03-31 09:23:57.067025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebbf26ec8813'
down_revision: Union[str, None] = 'c9ceec07b923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    if not column_exists('Request', 'Feedback_To_Requester'):
        op.add_column('Request', sa.Column('Feedback_To_Requester', sa.String(), nullable=True))
    
    if not column_exists('Request', 'Receiver'):
        op.add_column('Request', sa.Column('Receiver', sa.String(), nullable=True))
    
    if not column_exists('Request', 'Manufacturing_Destination'):
        op.add_column('Request', sa.Column('Manufacturing_Destination', sa.Boolean(), nullable=True))


def downgrade():
    if column_exists('Request', 'Feedback_To_Requester'):
        op.drop_column('Request', 'Feedback_To_Requester')
    
    if column_exists('Request', 'Receiver'):
        op.drop_column('Request', 'Receiver')
    
    if column_exists('Request', 'Manufacturing_Destination'):
        op.drop_column('Request', 'Manufacturing_Destination')
