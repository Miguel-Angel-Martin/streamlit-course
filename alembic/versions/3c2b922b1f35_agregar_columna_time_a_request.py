"""Agregar columna Time a Request

Revision ID: 3c2b922b1f35
Revises: 79897e625e37
Create Date: 2025-03-19 12:56:21.705069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c2b922b1f35'
down_revision: Union[str, None] = '79897e625e37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    if not column_exists('Request', 'Time'):
        op.add_column('Request', sa.Column('Time', sa.Time(), nullable=True))

def downgrade():
    if column_exists('Request', 'Time'):
        op.drop_column('Request', 'Time')
