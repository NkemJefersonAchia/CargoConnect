"""add dropoff_lat and dropoff_lng to bookings table

Revision ID: a3f1c2e4b5d6
Revises:
Create Date: 2026-03-15

needed these so the tracking page can pin the drop-off location
on the leaflet map when coordinates are available - Teniola
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers used by Alembic
revision = 'a3f1c2e4b5d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bookings', sa.Column('dropoff_lat', sa.Float(), nullable=True))
    op.add_column('bookings', sa.Column('dropoff_lng', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('bookings', 'dropoff_lng')
    op.drop_column('bookings', 'dropoff_lat')
