"""create keyword table

Revision ID: 9e7485c4a14b
Revises: 
Create Date: 2025-03-17 13:26:39.034150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e7485c4a14b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS "Keyword" (
        "Id" INTEGER NOT NULL, 
        "Keyword" VARCHAR NOT NULL, 
        PRIMARY KEY ("Id"), 
        UNIQUE ("Keyword")
    )
    """)

def downgrade():
    op.drop_table("Keyword")
