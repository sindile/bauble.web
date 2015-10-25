import flask
from faker import Faker

import pytest
import requests_mock
import sqlalchemy as sa
import sqlalchemy.orm as orm

import bauble
import bauble.db as db

faker = Faker()

@pytest.yield_fixture(scope="session", autouse=True)
def req_mock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.yield_fixture(scope='session', autouse=True)
def app():
    # this fixture is needed by the pytext-fixtures "client" fixture
    if flask.has_app_context():
        # tests probably started from ./manage.py
        _app = flask.current_app
    else:
        # tests probably started from py.test
        _app = bauble.create_app('../env/test.py')

    with _app.app_context():
        _app.testing = True
        yield _app


@pytest.yield_fixture
def session():
    # keep our test session separate from the thread local db.Session
    #session = db.Session()
    session = db.session()
    session.to_delete = set()

    @sa.event.listens_for(session, 'after_attach')
    def receive_after_attach(session, instance):
        session.to_delete.update([t.name for t in orm.object_mapper(instance).tables])

    try:
        yield session
    finally:
        session.rollback()

        # don't delete session scoped tables
        session.to_delete -= {'product_variety', 'product_category',
                              'product_variety_category', 'product_type'}

        # if len(to_delete) > 0:
        #     to_delete = ','.join(['public.{}'.format(t) for t in to_delete])
        #     print('truncate {}'.format(to_delete))
        #     session.execute('truncate {} cascade;'.format(to_delete))

        # sort table names first to avoid fk conflicts
        sorted_table_names = [t.name for t in db.metadata.sorted_tables]
        sort_key = lambda t: sorted_table_names.index(t)
        to_delete = sorted(session.to_delete, key=sort_key, reverse=True)
        for t in to_delete:
            session.execute('delete from public.{} *;'.format(t))
            #session.execute('truncate public.{} cascade;'.format(t))

        session.commit()
        session.close()


@pytest.fixture()
def family():
    from bauble.models import Family
    return Family(family=faker.first_name())


@pytest.fixture()
def genus(family):
    from bauble.models import Genus
    return Genus(genus=faker.first_name(), family=family)