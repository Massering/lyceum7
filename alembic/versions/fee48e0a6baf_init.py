"""Init

Revision ID: fee48e0a6baf
Revises: 
Create Date: 2021-04-05 18:04:21.995408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fee48e0a6baf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('news',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('creation_time', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('association',
    sa.Column('news', sa.Integer(), nullable=True),
    sa.Column('category', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['news'], ['news.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    op.drop_table('news')
    op.drop_table('categories')
    # ### end Alembic commands ###
