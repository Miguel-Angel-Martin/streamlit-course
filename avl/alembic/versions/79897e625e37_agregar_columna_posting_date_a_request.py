"""Agregar columna Posting_date a Request

Revision ID: 79897e625e37
Revises: 9e7485c4a14b
Create Date: 2025-03-19 12:54:32.189094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79897e625e37'
down_revision: Union[str, None] = '9e7485c4a14b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    if not column_exists('Request', 'Posting_date'):
        op.add_column('Request', sa.Column('Posting_date', sa.Date(), nullable=True))


def downgrade():
    if column_exists('Request', 'Posting_date'):
        op.drop_column('Request', 'Posting_date')