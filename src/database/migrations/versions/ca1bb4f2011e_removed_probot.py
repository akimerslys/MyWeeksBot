"""removed probot

Revision ID: ca1bb4f2011e
Revises: c86cd4adf9d9
Create Date: 2024-04-29 23:29:03.489668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ca1bb4f2011e'
down_revision: Union[str, None] = 'c86cd4adf9d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prousers')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prousers',
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('language_code', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('timezone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('tier', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tournaments', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True),
    sa.Column('is_premium', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('premium_until', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_blocked', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text("timezone('utc'::text, now())"), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text("timezone('utc'::text, now())"), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('user_id', 'id', name='prousers_pkey'),
    sa.UniqueConstraint('user_id', name='prousers_user_id_key')
    )
    # ### end Alembic commands ###
