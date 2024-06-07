"""empty message

Revision ID: 4cccd05e89f4
Revises: 86a280ad0fd2
Create Date: 2024-06-07 08:38:34.102096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cccd05e89f4'
down_revision = '86a280ad0fd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('client_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('client_toll', sa.Float(), nullable=True))
        batch_op.create_foreign_key(None, 'client', ['client_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activation', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('client_toll')
        batch_op.drop_column('client_id')

    # ### end Alembic commands ###
