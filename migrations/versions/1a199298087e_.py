"""Add publish delay

Revision ID: 1a199298087e
Revises:
Create Date: 2019-08-29 17:38:44.980289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a199298087e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('result', sa.Column('published_at', sa.DateTime(),
                                      nullable=True))
    published_at = sa.sql.column('published_at')
    result = sa.sql.table('result', published_at)
    created_at = sa.sql.column('created_at')
    op.execute(result
               .update()
               .values({published_at: created_at}))
    op.alter_column('result', 'published_at', existing_type=sa.DateTime(),
                    nullable=False)


def downgrade():
    op.drop_column('result', 'published_at')
