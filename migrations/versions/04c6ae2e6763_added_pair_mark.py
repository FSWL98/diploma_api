"""added pair mark

Revision ID: 04c6ae2e6763
Revises: 6a2db6f7462b
Create Date: 2022-05-15 20:24:49.598505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04c6ae2e6763'
down_revision = '6a2db6f7462b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pairing_mark',
    sa.Column('pairing_mark_id', sa.Integer(), nullable=False),
    sa.Column('criteria_id', sa.Integer(), nullable=True),
    sa.Column('staff_id', sa.Integer(), nullable=True),
    sa.Column('first_solution_id', sa.Integer(), nullable=True),
    sa.Column('second_solution_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('last_change_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['criteria_id'], ['criteria.criteria_id'], ),
    sa.ForeignKeyConstraint(['first_solution_id'], ['solution.solution_id'], ),
    sa.ForeignKeyConstraint(['second_solution_id'], ['solution.solution_id'], ),
    sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
    sa.PrimaryKeyConstraint('pairing_mark_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pairing_mark')
    # ### end Alembic commands ###