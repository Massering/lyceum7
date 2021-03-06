"""правки

Revision ID: ff7c5f918dfd
Revises: a917511a544b
Create Date: 2021-04-24 16:03:25.034311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff7c5f918dfd'
down_revision = 'a917511a544b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_awards_id'), 'awards', ['id'], unique=False)
    op.add_column('news', sa.Column('paths_to_images', sa.String(), nullable=True))
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.alter_column('news', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('news', 'content',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('news', 'paths_to_images')
    op.drop_index(op.f('ix_awards_id'), table_name='awards')
    op.alter_column('awards', 'direction',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('awards', 'description')
    op.drop_column('awards', 'creation_date')
    op.create_table('association',
    sa.Column('news', sa.INTEGER(), nullable=True),
    sa.Column('category', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['category'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['news'], ['news.id'], )
    )
    op.create_table('categories',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
