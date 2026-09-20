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
    Add users table and user_id (NOT NULL, FK -> users.id) to applications.

    SQLite does not support ALTER COLUMN for NOT NULL enforcement after the
    fact, so Alembic's batch_alter_table (which recreates the table) is used.

    LEGACY DATA POLICY — NO SILENT DATA DELETION:
    If any applications exist without a valid user_id (i.e. they pre-date the
    auth system), this migration will ABORT with a clear error rather than
    silently deleting those records.

    To migrate legacy applications to a specific owner before running this:

        UPDATE applications SET user_id = <owner_user_id>
        WHERE user_id IS NULL;

    Only then re-run: alembic upgrade head
    """
    # -------------------------------------------------------------------
    # 1. Create the users table (safe to re-run; CREATE TABLE IF NOT EXISTS
    #    is handled by Alembic checking existing tables).
    # -------------------------------------------------------------------
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
    # 2. Add user_id column to applications as NULLABLE first.
    # -------------------------------------------------------------------
    with op.batch_alter_table("applications", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_applications_user_id", ["user_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_applications_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )

    # -------------------------------------------------------------------
    # 3. SAFETY CHECK — refuse to proceed if legacy orphaned rows exist.
    #    This surfaces the problem explicitly instead of silently deleting data.
    # -------------------------------------------------------------------
    conn = op.get_bind()
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

    # -------------------------------------------------------------------
    # 4. Enforce NOT NULL now that no orphaned rows remain.
    # -------------------------------------------------------------------
    with op.batch_alter_table("applications", schema=None) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    """Remove user_id from applications and drop users table (non-destructive to app data)."""
    with op.batch_alter_table("applications", schema=None) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint("fk_applications_user_id_users", type_="foreignkey")
        batch_op.drop_index("ix_applications_user_id")
        batch_op.drop_column("user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
