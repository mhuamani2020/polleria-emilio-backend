"""increase refresh_token column to 1024 chars

Revision ID: 003
Revises: 002
Create Date: 2026-05-26 18:20:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("user_sessions", "refresh_token", type_=sa.String(1024), nullable=False)


def downgrade() -> None:
    op.alter_column("user_sessions", "refresh_token", type_=sa.String(255), nullable=False)
