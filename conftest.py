import os
import tempfile

import pytest

from counter import app as flask_app, db, Counter, log_file


@pytest.fixture(scope="session", autouse=True)
def _test_env():
    # тестовая БД в памяти / временном файле
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("COUNTER_PORT", "5001")
    yield


@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Тестовый экземпляр приложения.
    """
    test_log_file = tmp_path / "counter.log"
    monkeypatch.setattr("counter.log_file", str(test_log_file), raising=False)

    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(Counter(count=0))
        db.session.commit()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Тестовый клиент Flask.
    """
    return app.test_client()


@pytest.fixture
def app_context(app):
    """
    Контекст приложения для работы с БД в тестах.
    """
    with app.app_context():
        yield

