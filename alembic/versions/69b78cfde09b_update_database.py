"""update-database

Revision ID: 69b78cfde09b
Revises: 0b80cbd89e7b
Create Date: 2024-08-20 23:16:05.237191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69b78cfde09b'
down_revision: Union[str, None] = '0b80cbd89e7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(), nullable=False))
    op.add_column('users', sa.Column('sex', sa.String(), nullable=False))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'age')
    op.drop_column('users', 'sex')
    op.drop_column('users', 'name')
    # ### end Alembic commands ###
