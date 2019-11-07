"""empty message

Revision ID: bd2c238a9630
Revises: 89b29860b313
Create Date: 2019-11-06 14:11:48.438256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd2c238a9630'
down_revision = '89b29860b313'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sku', sa.Column('sku_discount_desc', sa.String(length=3), nullable=True))
    op.add_column('sku', sa.Column('sku_html_1', sa.String(), nullable=True))
    op.add_column('sku', sa.Column('sku_html_2', sa.String(), nullable=True))
    op.add_column('sku', sa.Column('sku_html_3', sa.String(), nullable=True))
    op.add_column('sku', sa.Column('sku_lowercase', sa.String(length=100), nullable=True))
    op.add_column('sku', sa.Column('sku_price_asc', sa.String(length=10), nullable=True))
    op.add_column('sku', sa.Column('sku_price_desc', sa.String(length=10), nullable=True))
    op.add_column('sku', sa.Column('sku_twin', sa.Boolean(), nullable=True))
    op.add_column('sku', sa.Column('sku_type', sa.String(length=5), nullable=True))
    op.create_index(op.f('ix_sku_sku_lowercase'), 'sku', ['sku_lowercase'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sku_sku_lowercase'), table_name='sku')
    op.drop_column('sku', 'sku_type')
    op.drop_column('sku', 'sku_twin')
    op.drop_column('sku', 'sku_price_desc')
    op.drop_column('sku', 'sku_price_asc')
    op.drop_column('sku', 'sku_lowercase')
    op.drop_column('sku', 'sku_html_3')
    op.drop_column('sku', 'sku_html_2')
    op.drop_column('sku', 'sku_html_1')
    op.drop_column('sku', 'sku_discount_desc')
    # ### end Alembic commands ###
