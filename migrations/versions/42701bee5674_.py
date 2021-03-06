"""empty message

Revision ID: 42701bee5674
Revises: 5f3e83fe6f8f
Create Date: 2020-01-15 11:38:01.294660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42701bee5674'
down_revision = '5f3e83fe6f8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('db_status', 'status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('db_status', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
