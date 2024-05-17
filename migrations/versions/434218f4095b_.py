"""empty message

Revision ID: 434218f4095b
Revises: 0d5f6e547e4e
Create Date: 2024-05-09 16:26:00.079888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '434218f4095b'
down_revision = '0d5f6e547e4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('sales_request')
    op.drop_table('users')
    op.drop_table('reports')
    op.drop_table('log')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('action', sa.VARCHAR(length=255), nullable=False),
    sa.Column('timestamp', sa.VARCHAR(length=20), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reports',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('client_name', sa.VARCHAR(length=120), nullable=False),
    sa.Column('reason', sa.VARCHAR(length=20), nullable=False),
    sa.Column('billing', sa.VARCHAR(length=20), nullable=False),
    sa.Column('model', sa.VARCHAR(length=120), nullable=False),
    sa.Column('customization', sa.TEXT(), nullable=False),
    sa.Column('equipment_number', sa.VARCHAR(length=20), nullable=False),
    sa.Column('problem_type', sa.VARCHAR(length=50), nullable=False),
    sa.Column('photos', sa.VARCHAR(length=255), nullable=True),
    sa.Column('treatment', sa.VARCHAR(length=50), nullable=False),
    sa.Column('status', sa.VARCHAR(length=20), nullable=False),
    sa.Column('date_completed', sa.VARCHAR(length=20), nullable=True),
    sa.Column('image_paths', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=100), nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=False),
    sa.Column('profile_picture', sa.VARCHAR(length=100), nullable=True),
    sa.Column('additional_info', sa.TEXT(), nullable=True),
    sa.Column('access_level', sa.VARCHAR(length=20), nullable=True),
    sa.Column('unread_notifications', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('sales_request',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_completed', sa.VARCHAR(length=20), nullable=True),
    sa.Column('cnpj', sa.VARCHAR(length=20), nullable=True),
    sa.Column('contract_start', sa.VARCHAR(length=20), nullable=True),
    sa.Column('vigency', sa.VARCHAR(length=20), nullable=True),
    sa.Column('reason', sa.VARCHAR(length=50), nullable=True),
    sa.Column('location', sa.VARCHAR(length=100), nullable=True),
    sa.Column('equipment_numbers', sa.VARCHAR(length=200), nullable=True),
    sa.Column('client', sa.VARCHAR(length=120), nullable=True),
    sa.Column('sales_rep', sa.VARCHAR(length=50), nullable=True),
    sa.Column('contract_type', sa.VARCHAR(length=50), nullable=True),
    sa.Column('shipping', sa.VARCHAR(length=50), nullable=True),
    sa.Column('delivery_fee', sa.FLOAT(), nullable=True),
    sa.Column('address', sa.VARCHAR(length=200), nullable=True),
    sa.Column('contact_person', sa.VARCHAR(length=100), nullable=True),
    sa.Column('email', sa.VARCHAR(length=120), nullable=True),
    sa.Column('phone', sa.VARCHAR(length=20), nullable=True),
    sa.Column('quantity', sa.INTEGER(), nullable=True),
    sa.Column('model', sa.VARCHAR(length=50), nullable=True),
    sa.Column('customization', sa.VARCHAR(length=100), nullable=True),
    sa.Column('tp', sa.VARCHAR(length=50), nullable=True),
    sa.Column('charger', sa.VARCHAR(length=100), nullable=True),
    sa.Column('cable', sa.VARCHAR(length=100), nullable=True),
    sa.Column('invoice_type', sa.VARCHAR(length=50), nullable=True),
    sa.Column('value', sa.VARCHAR(length=50), nullable=True),
    sa.Column('total_value', sa.VARCHAR(length=50), nullable=True),
    sa.Column('payment_method', sa.VARCHAR(length=50), nullable=True),
    sa.Column('observations', sa.TEXT(), nullable=True),
    sa.Column('accept_terms', sa.BOOLEAN(), nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), nullable=False),
    sa.Column('date_sent_to_customer', sa.VARCHAR(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('type', sa.VARCHAR(length=50), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=False),
    sa.Column('viewed', sa.BOOLEAN(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
