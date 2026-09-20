"""create_users_and_applications_tables

Revision ID: 4750db534165
Revises: 
Create Date: 2026-09-20 23:55:43.858773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "4750db534165"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ensure users and applications tables exist with proper schema and relationships.

    HANDLES TWO SCENARIOS SAFELY:
    1. Fresh Database (e.g. Railway PostgreSQL):
       Creates `users` table, then creates `applications` table with all columns,
       indexes, and foreign key constraint (user_id -> users.id).

    2. Existing Database with legacy `applications` table:
       Adds `users` table, adds `user_id` to `applications`, validates that no
       orphaned rows exist (refuses to delete legacy data silently), and enforces
       NOT NULL on `user_id`.
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # -------------------------------------------------------------------
    # 1. Create the users table if it does not exist
    # -------------------------------------------------------------------
    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id", name="pk_users"),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    # -------------------------------------------------------------------
    # 2. Handle applications table
    # -------------------------------------------------------------------
    if "applications" not in existing_tables:
        # Fresh production database — create applications table directly
        op.create_table(
            "applications",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company", sa.String(length=200), nullable=False),
            sa.Column("job_title", sa.String(length=200), nullable=False),
            sa.Column("job_description", sa.Text(), nullable=True),
            sa.Column("application_date", sa.Date(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="saved"),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("interview_date", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id", name="pk_applications"),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_applications_user_id_users",
            ),
        )
        op.create_index("ix_applications_id", "applications", ["id"], unique=False)
        op.create_index("ix_applications_company", "applications", ["company"], unique=False)
        op.create_index("ix_applications_job_title", "applications", ["job_title"], unique=False)
        op.create_index("ix_applications_status", "applications", ["status"], unique=False)
        op.create_index("ix_applications_user_id", "applications", ["user_id"], unique=False)
    else:
        # Existing database: inspect columns to see if user_id migration is needed
        columns = [c["name"] for c in inspector.get_columns("applications")]
        if "user_id" not in columns:
            with op.batch_alter_table("applications", schema=None) as batch_op:
                batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
                batch_op.create_index("ix_applications_user_id", ["user_id"], unique=False)
                batch_op.create_foreign_key(
                    "fk_applications_user_id_users",
                    "users",
                    ["user_id"],
                    ["id"],
                )

            # SAFETY CHECK — refuse to proceed if legacy orphaned rows exist
            orphaned_count = conn.execute(
                text("SELECT COUNT(*) FROM applications WHERE user_id IS NULL")
            ).scalar()

            if orphaned_count and orphaned_count > 0:
                raise RuntimeError(
                    f"\n\n"
                    f"  MIGRATION ABORTED — DATA LOSS PREVENTION\n"
                    f"  =========================================\n"
                    f"  Found {orphaned_count} application row(s) with no owner (user_id IS NULL).\n"
                    f"  Silently deleting existing data is not permitted.\n\n"
                    f"  To resolve, assign these rows to a valid user before re-running:\n\n"
                    f"    UPDATE applications SET user_id = <owner_user_id> WHERE user_id IS NULL;\n\n"
                    f"  Then run:  alembic upgrade head\n"
                )

            with op.batch_alter_table("applications", schema=None) as batch_op:
                batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    """Downgrade schema safely."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "applications" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("applications")]
        if "user_id" in columns:
            with op.batch_alter_table("applications", schema=None) as batch_op:
                batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=True)
                batch_op.drop_constraint("fk_applications_user_id_users", type_="foreignkey")
                batch_op.drop_index("ix_applications_user_id")
                batch_op.drop_column("user_id")

    if "users" in existing_tables:
        op.drop_index("ix_users_email", table_name="users")
        op.drop_index("ix_users_id", table_name="users")
        op.drop_table("users")
