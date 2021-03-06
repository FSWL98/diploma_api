"""added solution and solution evaluating tables

Revision ID: 6a2db6f7462b
Revises: dc7a0e972763
Create Date: 2022-02-21 16:09:33.430860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a2db6f7462b'
down_revision = 'dc7a0e972763'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('criteria',
    sa.Column('criteria_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('minimum', sa.Integer(), nullable=False),
    sa.Column('maximum', sa.Integer(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('last_change_by_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('criteria_id')
    )
    op.create_table('solution',
    sa.Column('solution_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('user_event_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('last_change_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['Event.event_id'], ),
    sa.ForeignKeyConstraint(['user_event_id'], ['user_event.user_event_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('solution_id')
    )
    op.create_table('mark',
    sa.Column('mark_id', sa.Integer(), nullable=False),
    sa.Column('criteria_id', sa.Integer(), nullable=True),
    sa.Column('staff_id', sa.Integer(), nullable=True),
    sa.Column('solution_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('last_change_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['criteria_id'], ['criteria.criteria_id'], ),
    sa.ForeignKeyConstraint(['solution_id'], ['solution.solution_id'], ),
    sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
    sa.PrimaryKeyConstraint('mark_id')
    )
    op.add_column('Event', sa.Column('last_change_by_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'api_key', ['key'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'api_key', type_='unique')
    op.drop_column('Event', 'last_change_by_id')
    op.drop_table('mark')
    op.drop_table('solution')
    op.drop_table('criteria')
    # ### end Alembic commands ###
