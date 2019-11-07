"""empty message

Revision ID: 264eab67f6ec
Revises: 912d014ca8d7
Create Date: 2019-11-06 15:26:29.892362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '264eab67f6ec'
down_revision = '912d014ca8d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sku', sa.Column('sku_type', sa.String(length=13), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sku', 'sku_type')
    # ### end Alembic commands ###
