"""add display_name, dni, phone, shift to users

Revision ID: 002
Revises: 001
Create Date: 2026-05-26 09:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("dni", sa.String(8), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("shift", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "shift")
    op.drop_column("users", "phone")
    op.drop_column("users", "dni")
    op.drop_column("users", "display_name")
