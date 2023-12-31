"""Added unique_key field

Revision ID: 7bc6726fac4d
Revises: 
Create Date: 2023-11-26 17:47:32.824985

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7bc6726fac4d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('captcha_result', schema=None) as batch_op:
        batch_op.alter_column('captcha_type',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.String(length=120),
               existing_nullable=False)

    with op.batch_alter_table('user_test', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unique_key', sa.String(length=120), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_test', schema=None) as batch_op:
        batch_op.drop_column('unique_key')

    with op.batch_alter_table('captcha_result', schema=None) as batch_op:
        batch_op.alter_column('captcha_type',
               existing_type=sa.String(length=120),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###
