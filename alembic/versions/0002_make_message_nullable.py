"""make message nullable

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-06
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("contact_submissions", "message", nullable=True)


def downgrade() -> None:
    op.execute("UPDATE contact_submissions SET message = '' WHERE message IS NULL")
    op.alter_column("contact_submissions", "message", nullable=False)
