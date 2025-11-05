import hashlib

from fastapi.testclient import TestClient

from services.api import main


class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.ping_called = False

    def ping(self):
        self.ping_called = True
        return True

    def setex(self, key, ttl, value):
        self.storage[key] = (value, ttl)
        return True

    def get(self, key):
        entry = self.storage.get(key)
        if entry is None:
            return None
        return entry[0]


def make_client(fake_redis):
    main.redis_client = fake_redis
    return TestClient(main.app)


def test_healthz_ok():
    fake = FakeRedis()
    client = make_client(fake)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert fake.ping_called is True


def test_shorten_and_resolve():
    fake = FakeRedis()
    client = make_client(fake)

    url = "https://example.com"
    response = client.post("/shorten", json={"url": url})
    assert response.status_code == 200

    expected_code = hashlib.sha1(url.encode("utf-8")).hexdigest()[:7]
    assert response.json() == {"code": expected_code}

    key = f"url:{expected_code}"
    assert key in fake.storage
    stored_url, ttl = fake.storage[key]
    assert stored_url == url
    assert ttl == main.REDIS_TTL

    resolved = client.get(f"/r/{expected_code}")
    assert resolved.status_code == 200
    assert resolved.json() == {"url": url}


def test_resolve_not_found():
    fake = FakeRedis()
    client = make_client(fake)

    response = client.get("/r/missing")
    assert response.status_code == 404
