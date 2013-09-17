from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
request = Table('request', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('proj_id', Integer),
    Column('requester_id', Integer),
)

project = Table('project', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('about', String(length=400)),
    Column('help', String(length=400)),
    Column('description', String(length=400)),
    Column('progress', String(length=15)),
    Column('user_id', Integer),
    Column('following', String(length=400)),
    Column('members', String(length=400)),
    Column('photo_exists', SmallInteger, default=ColumnDefault(0)),
    Column('photo_file', LargeBinary(length=1000000)),
    Column('photo_name', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].create()
    post_meta.tables['project'].columns['following'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].drop()
    post_meta.tables['project'].columns['following'].drop()
