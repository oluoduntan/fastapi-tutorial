"""create phone number for user table

Revision ID: a5c62a53f106
Revises: 
Create Date: 2024-11-29 18:13:33.744318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5c62a53f106'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('phone_number', sa.String, nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('user', 'phone_number')
    pass
