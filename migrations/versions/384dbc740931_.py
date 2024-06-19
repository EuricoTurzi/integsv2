"""empty message

Revision ID: 384dbc740931
Revises: 
Create Date: 2024-06-17 14:08:28.124692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '384dbc740931'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('km_allowance', sa.Integer(), nullable=True),
    sa.Column('hour_allowance', sa.Time(), nullable=True),
    sa.Column('activation_value', sa.Float(), nullable=True),
    sa.Column('km_excess_value', sa.Float(), nullable=True),
    sa.Column('excess_value', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entrance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=True),
    sa.Column('client', sa.String(length=120), nullable=False),
    sa.Column('entrance_type', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=True),
    sa.Column('customization', sa.String(length=100), nullable=True),
    sa.Column('type_of_receipt', sa.String(length=50), nullable=False),
    sa.Column('recipients_name', sa.String(length=50), nullable=True),
    sa.Column('withdrawn_by', sa.String(length=50), nullable=True),
    sa.Column('equipment_numbers', sa.String(length=200), nullable=False),
    sa.Column('maintenance_status', sa.String(length=50), nullable=True),
    sa.Column('returned_equipment_numbers', sa.String(length=200), nullable=True),
    sa.Column('accept_terms', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment_stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=True),
    sa.Column('quantity_in_stock', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('km_allowance', sa.Integer(), nullable=True),
    sa.Column('hour_allowance', sa.Time(), nullable=True),
    sa.Column('activation_value', sa.Float(), nullable=True),
    sa.Column('km_excess_value', sa.Float(), nullable=True),
    sa.Column('excess_value', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reactivation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=True),
    sa.Column('client', sa.String(length=120), nullable=False),
    sa.Column('reactivation_reason', sa.String(length=120), nullable=False),
    sa.Column('request_channel', sa.String(length=90), nullable=False),
    sa.Column('value', sa.String(length=50), nullable=False),
    sa.Column('total_value', sa.String(length=50), nullable=False),
    sa.Column('observation', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_name', sa.String(length=120), nullable=False),
    sa.Column('reason', sa.String(length=20), nullable=False),
    sa.Column('billing', sa.String(length=20), nullable=False),
    sa.Column('model', sa.String(length=120), nullable=False),
    sa.Column('customization', sa.String(length=120), nullable=False),
    sa.Column('equipment_number', sa.String(length=20), nullable=False),
    sa.Column('problem_type', sa.String(length=50), nullable=False),
    sa.Column('photos', sa.String(length=255), nullable=True),
    sa.Column('treatment', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('date_completed', sa.String(length=20), nullable=True),
    sa.Column('image_paths', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sales_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_completed', sa.String(length=20), nullable=True),
    sa.Column('cnpj', sa.String(length=20), nullable=True),
    sa.Column('contract_start', sa.String(length=20), nullable=True),
    sa.Column('vigency', sa.String(length=20), nullable=True),
    sa.Column('reason', sa.String(length=50), nullable=True),
    sa.Column('location', sa.String(length=50), nullable=True),
    sa.Column('maintenance_number', sa.String(length=100), nullable=True),
    sa.Column('client', sa.String(length=120), nullable=True),
    sa.Column('sales_rep', sa.String(length=50), nullable=True),
    sa.Column('contract_type', sa.String(length=50), nullable=True),
    sa.Column('shipping', sa.String(length=50), nullable=True),
    sa.Column('delivery_fee', sa.Numeric(precision=16, scale=2), nullable=True),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('contact_person', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('model', sa.String(length=50), nullable=True),
    sa.Column('customization', sa.String(length=100), nullable=True),
    sa.Column('tp', sa.String(length=50), nullable=True),
    sa.Column('charger', sa.String(length=100), nullable=True),
    sa.Column('cable', sa.String(length=100), nullable=True),
    sa.Column('invoice_type', sa.String(length=50), nullable=True),
    sa.Column('value', sa.Numeric(precision=16, scale=2), nullable=True),
    sa.Column('total_value', sa.Numeric(precision=16, scale=2), nullable=True),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('observations', sa.Text(), nullable=True),
    sa.Column('accept_terms', sa.Boolean(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('date_sent_to_customer', sa.String(length=20), nullable=True),
    sa.Column('equipment_numbers', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('profile_picture', sa.String(length=100), nullable=True),
    sa.Column('additional_info', sa.Text(), nullable=True),
    sa.Column('access_level', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('activation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('provider_id', sa.Integer(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('plates', sa.String(length=50), nullable=True),
    sa.Column('agents', sa.String(length=50), nullable=True),
    sa.Column('equipment_id', sa.String(length=50), nullable=True),
    sa.Column('initial_km', sa.Integer(), nullable=True),
    sa.Column('final_km', sa.Integer(), nullable=True),
    sa.Column('toll', sa.Float(), nullable=True),
    sa.Column('client_toll', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name='fk_client_id'),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reactivation_id', sa.Integer(), nullable=False),
    sa.Column('equipment_id', sa.String(length=100), nullable=False),
    sa.Column('equipment_ccid', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['reactivation_id'], ['reactivation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('timestamp', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('log')
    op.drop_table('equipment')
    op.drop_table('activation')
    op.drop_table('users')
    op.drop_table('sales_request')
    op.drop_table('reports')
    op.drop_table('reactivation')
    op.drop_table('provider')
    op.drop_table('equipment_stock')
    op.drop_table('entrance')
    op.drop_table('client')
    # ### end Alembic commands ###