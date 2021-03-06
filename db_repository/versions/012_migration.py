from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('user_name', String(length=64)),
    Column('major', String(length=64)),
    Column('minor', String(length=64)),
    Column('email', String(length=120)),
    Column('password', String(length=64)),
    Column('year', String(length=64)),
    Column('photo_exists', SmallInteger, default=ColumnDefault(0)),
    Column('photo_file', LargeBinary(length=1000000)),
    Column('photo_name', String(length=64)),
    Column('progress', String(length=64)),
    Column('activated', SmallInteger, default=ColumnDefault(0)),
    Column('member_of', String(length=500)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['photo_name'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['photo_name'].drop()
