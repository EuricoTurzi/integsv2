"""empty message

Revision ID: a872ca0d2f91
Revises: dea9fe36c390
Create Date: 2024-05-24 10:45:54.299290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a872ca0d2f91'
down_revision = 'dea9fe36c390'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_request', schema=None) as batch_op:
        batch_op.alter_column('delivery_fee',
               existing_type=sa.FLOAT(),
               type_=sa.Numeric(precision=16, scale=2),
               existing_nullable=True)
        batch_op.alter_column('value',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.Numeric(precision=16, scale=2),
               existing_nullable=True)
        batch_op.alter_column('total_value',
               existing_type=sa.NUMERIC(precision=12, scale=2),
               type_=sa.Numeric(precision=16, scale=2),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_request', schema=None) as batch_op:
        batch_op.alter_column('total_value',
               existing_type=sa.Numeric(precision=16, scale=2),
               type_=sa.NUMERIC(precision=12, scale=2),
               existing_nullable=True)
        batch_op.alter_column('value',
               existing_type=sa.Numeric(precision=16, scale=2),
               type_=sa.NUMERIC(precision=10, scale=2),
               existing_nullable=True)
        batch_op.alter_column('delivery_fee',
               existing_type=sa.Numeric(precision=16, scale=2),
               type_=sa.FLOAT(),
               existing_nullable=True)

    # ### end Alembic commands ###
