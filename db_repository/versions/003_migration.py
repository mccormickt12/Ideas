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
    Column('username', String(length=64)),
    Column('skills', String(length=400)),
    Column('reason', String(length=400)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].columns['reason'].create()
    post_meta.tables['request'].columns['skills'].create()
    post_meta.tables['request'].columns['username'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].columns['reason'].drop()
    post_meta.tables['request'].columns['skills'].drop()
    post_meta.tables['request'].columns['username'].drop()
