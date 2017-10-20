from saseumn import make_app
import pytest


@pytest.yield_fixture(scope="session")
def app():
    app = make_app(testing=True)
    context = app.app_context()
    context.push()
    yield app
    context.pop()


@pytest.fixture(scope="function")
def db(app, request):
    def teardown():
        app.db.drop_all()
    app.db.create_all()
    request.addfinalizer(teardown)
    return app.db


@pytest.fixture()
def client(app, db):
    return app.test_client()
