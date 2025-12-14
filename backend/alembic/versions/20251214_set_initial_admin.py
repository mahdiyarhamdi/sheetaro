"""Set initial admin user.

Revision ID: 20251214_admin
Revises: 20251214_c2c
Create Date: 2025-12-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251214_admin'
down_revision: Union[str, None] = '20251214_c2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Initial admin telegram ID
INITIAL_ADMIN_TELEGRAM_ID = 390473938


def upgrade() -> None:
    # Set the user with this telegram_id as admin if they exist
    op.execute(
        f"""
        UPDATE users 
        SET role = 'ADMIN' 
        WHERE telegram_id = {INITIAL_ADMIN_TELEGRAM_ID}
        """
    )


def downgrade() -> None:
    # Revert to customer role
    op.execute(
        f"""
        UPDATE users 
        SET role = 'CUSTOMER' 
        WHERE telegram_id = {INITIAL_ADMIN_TELEGRAM_ID}
        """
    )

