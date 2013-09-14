from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
project = Table('project', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('description', String(length=400)),
    Column('user_id', Integer),
    Column('members', String(length=400)),
    Column('photo_exists', SmallInteger, default=ColumnDefault(0)),
    Column('photo_file', LargeBinary(length=1000000)),
    Column('photo_name', String(length=64)),
)

user = Table('user', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('user_name', String),
    Column('major', String),
    Column('minor', String),
    Column('email', String),
    Column('password', String),
    Column('year', String),
    Column('photo_exists', SmallInteger),
    Column('photo_file', LargeBinary),
    Column('progress', String),
    Column('activated', SmallInteger),
    Column('member_of', String),
    Column('photo_name', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].columns['photo_exists'].create()
    post_meta.tables['project'].columns['photo_file'].create()
    post_meta.tables['project'].columns['photo_name'].create()
    pre_meta.tables['user'].columns['photo_exists'].drop()
    pre_meta.tables['user'].columns['photo_file'].drop()
    pre_meta.tables['user'].columns['photo_name'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].columns['photo_exists'].drop()
    post_meta.tables['project'].columns['photo_file'].drop()
    post_meta.tables['project'].columns['photo_name'].drop()
    pre_meta.tables['user'].columns['photo_exists'].create()
    pre_meta.tables['user'].columns['photo_file'].create()
    pre_meta.tables['user'].columns['photo_name'].create()
