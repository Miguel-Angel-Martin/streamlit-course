"""Campos en la tabla Proyectos

Revision ID: c9ceec07b923
Revises: 3c2b922b1f35
Create Date: 2025-03-24 14:09:57.495300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9ceec07b923'
down_revision: Union[str, None] = '3c2b922b1f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    if not column_exists('Project', 'Name'):
        op.add_column('Project', sa.Column('Name', sa.String(), nullable=True))
    
    if not column_exists('Project', 'Manager'):
        op.add_column('Project', sa.Column('Manager', sa.String(), nullable=True))
    
    if not column_exists('Project', 'Closed'):
        op.add_column('Project', sa.Column('Closed', sa.Boolean(), nullable=True))
    
    if not column_exists('Project', 'Modified_DateTime'):
        op.add_column('Project', sa.Column('Modified_DateTime', sa.DateTime(), nullable=True))
    
    if not column_exists('Project', 'Modifier'):
        op.add_column('Project', sa.Column('Modifier', sa.String(), nullable=True))


def downgrade():
    if column_exists('Project', 'Name'):
        op.drop_column('Project', 'Name')
    
    if column_exists('Project', 'Manager'):
        op.drop_column('Project', 'Manager')
    
    if column_exists('Project', 'Closed'):
        op.drop_column('Project', 'Closed')
    
    if column_exists('Project', 'Modified_DateTime'):
        op.drop_column('Project', 'Modified_DateTime')
    
    if column_exists('Project', 'Modifier'):
        op.drop_column('Project', 'Modifier')
