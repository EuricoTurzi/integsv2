"""empty message

Revision ID: dea9fe36c390
Revises: bd287a9bc7f2
Create Date: 2024-05-24 10:37:04.274253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dea9fe36c390'
down_revision = 'bd287a9bc7f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_request', schema=None) as batch_op:
        batch_op.alter_column('value',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=True)
        batch_op.alter_column('total_value',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Numeric(precision=12, scale=2),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_request', schema=None) as batch_op:
        batch_op.alter_column('total_value',
               existing_type=sa.Numeric(precision=12, scale=2),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
        batch_op.alter_column('value',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###
