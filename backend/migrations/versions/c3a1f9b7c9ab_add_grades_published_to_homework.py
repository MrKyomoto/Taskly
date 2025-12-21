"""add grades_published field to homework

Revision ID: c3a1f9b7c9ab
Revises: b80bbc9c820b
Create Date: 2025-12-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3a1f9b7c9ab'
down_revision = 'b80bbc9c820b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('homework', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'grades_published',
                sa.Boolean(),
                server_default='0',
                nullable=False,
                comment='是否已发布成绩'
            )
        )


def downgrade():
    with op.batch_alter_table('homework', schema=None) as batch_op:
        batch_op.drop_column('grades_published')


