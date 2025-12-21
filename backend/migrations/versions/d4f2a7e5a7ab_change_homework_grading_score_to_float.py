"""change homework_grading.score to float

Revision ID: d4f2a7e5a7ab
Revises: c3a1f9b7c9ab
Create Date: 2025-12-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f2a7e5a7ab'
down_revision = 'c3a1f9b7c9ab'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('homework_grading', schema=None) as batch_op:
        batch_op.alter_column('score',
                              existing_type=sa.Integer(),
                              type_=sa.Float(),
                              existing_nullable=True)


def downgrade():
    with op.batch_alter_table('homework_grading', schema=None) as batch_op:
        batch_op.alter_column('score',
                              existing_type=sa.Float(),
                              type_=sa.Integer(),
                              existing_nullable=True)


