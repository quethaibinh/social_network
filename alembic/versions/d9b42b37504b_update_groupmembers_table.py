"""update groupmembers table

Revision ID: d9b42b37504b
Revises: d69c0787c0ec
Create Date: 2024-09-08 13:59:02.445998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9b42b37504b'
down_revision: Union[str, None] = 'd69c0787c0ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
