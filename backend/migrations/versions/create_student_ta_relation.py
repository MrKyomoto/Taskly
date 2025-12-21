"""create student ta relation table

Revision ID: create_student_ta_relation
Revises: d4f2a7e5a7ab
Create Date: 2024-12-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'create_student_ta_relation'
down_revision = 'd4f2a7e5a7ab'
branch_labels = None
depends_on = None


def upgrade():
    # 创建学生-课程助教关联表
    op.create_table(
        'student_ta_relation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='助教'),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['course.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'course_id', name='unique_student_ta_course')
    )
    op.create_index(op.f('ix_student_ta_relation_student_id'), 'student_ta_relation', ['student_id'], unique=False)
    op.create_index(op.f('ix_student_ta_relation_course_id'), 'student_ta_relation', ['course_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_student_ta_relation_course_id'), table_name='student_ta_relation')
    op.drop_index(op.f('ix_student_ta_relation_student_id'), table_name='student_ta_relation')
    op.drop_table('student_ta_relation')

