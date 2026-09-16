from counter import Counter, db

def test_index_status_code(client):
    """
    Проверка, что / отдаёт 200.
    """
    resp = client.get("/")
    assert resp.status_code == 200


def test_counter_increment(client, app_context):
    """
    При каждом GET / значение счётчика увеличивается на 1.
    """
    counter = Counter.query.first()
    assert counter is not None
    start = counter.count

    resp1 = client.get("/")
    assert resp1.status_code == 200

    counter = Counter.query.first()
    assert counter.count == start + 1

    resp2 = client.get("/")
    assert resp2.status_code == 200

    counter = Counter.query.first()
    assert counter.count == start + 2


def test_counter_persists_between_requests(client, app_context):
    """
    Счётчик сохраняется между разными запросами в рамках одного приложения.
    """
    client.get("/")
    client.get("/")
    client.get("/")

    counter = Counter.query.first()
    assert counter.count >= 3  # зависит от предыдущих тестов, но не должен быть 0


def test_index_renders_count_in_html(client):
    """
    Шаблон index.html содержит значение count (простейшая проверка).
    """
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.data.decode("utf-8")
    assert "count" in data.lower() or "счётчик" in data.lower()


def test_logging_to_file(tmp_path, monkeypatch, app):
    """
    Проверка, что запрос логируется в файл.
    """
    test_log_file = tmp_path / "counter.log"
    from counter import app as flask_app

    for h in list(flask_app.logger.handlers):
        flask_app.logger.removeHandler(h)

    import logging

    fh = logging.FileHandler(test_log_file)
    fh.setLevel(logging.INFO)
    flask_app.logger.addHandler(fh)
    flask_app.logger.setLevel(logging.INFO)

    client = flask_app.test_client()

    resp = client.get("/")
    assert resp.status_code == 200

    fh.flush()

    assert test_log_file.exists()
    content = test_log_file.read_text(encoding="utf-8")
    assert "Request GET" in content

