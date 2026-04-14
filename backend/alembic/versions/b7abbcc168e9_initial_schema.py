"""initial schema

Revision ID: b7abbcc168e9
Revises:
Create Date: <auto>
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b7abbcc168e9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enum type for booking status
    booking_status = postgresql.ENUM(
        "PENDING",
        "RESERVED",
        "REJECTED",
        "CANCELLED",
        "EXPIRED",
        name="booking_status",
        create_type=False,  # prevents auto-create during table creation
    )
    booking_status.create(op.get_bind(), checkfirst=True)

    # Admins table (JWT admin auth)
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_admins_username", "admins", ["username"], unique=True)

    # Bookings table (matches your current router/service fields)
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column("guest_name", sa.String(length=120), nullable=False),
        sa.Column("contact_number", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),

        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("pax", sa.Integer(), nullable=False),

        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("deposit_amount", sa.Integer(), nullable=False),

        sa.Column("receipt_path", sa.String(length=300), nullable=True),

        sa.Column("status", booking_status, nullable=False, server_default="PENDING"),
        sa.Column("booking_code", sa.String(length=20), nullable=False),

        sa.Column("hold_expires_at", sa.DateTime(), nullable=True),

        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),

        sa.Column("rejection_reason", sa.String(length=255), nullable=True),
        sa.Column("cancellation_reason", sa.String(length=255), nullable=True),

        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_bookings_event_date", "bookings", ["event_date"])
    op.create_index("ix_bookings_status", "bookings", ["status"])
    op.create_index("ix_bookings_booking_code", "bookings", ["booking_code"], unique=True)

    # Partial unique index: only ONE RESERVED per event_date
    op.execute(
        "CREATE UNIQUE INDEX uq_reserved_event_date "
        "ON bookings (event_date) "
        "WHERE status = 'RESERVED'::booking_status"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_reserved_event_date")

    op.drop_index("ix_bookings_booking_code", table_name="bookings")
    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_event_date", table_name="bookings")
    op.drop_table("bookings")

    op.drop_index("ix_admins_username", table_name="admins")
    op.drop_table("admins")

    op.execute("DROP TYPE IF EXISTS booking_status")