import threading
from uuid import uuid4

import pytest
from api.services.jwt_service import JWTService
from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from django.urls import re_path
from rest_framework.test import APIClient
from ws.consumers import RoomConsumer

User = get_user_model()


@pytest.fixture(autouse=True)
def test_settings(settings):
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def jwt_token():
    return JWTService().generate_token(str(uuid4))

@pytest.fixture
def user(db):
    return User.objects.create_user(username="user1", password="pass")

@pytest.fixture
def room(db):
    from rooms.models import Room

    return Room.objects.create(name="Test Room")


@pytest.fixture
def voting(db, room):
    from votings.models import Voting

    return Voting.objects.create(room=room, task_name="Initial Task")

@pytest.fixture
def finished_voting(db, room):
    from votings.models import Voting

    return Voting.objects.create(room=room, task_name="Initial Task", average_score=4)

@pytest.fixture
def room_url_router():
    application = URLRouter(
        [
            re_path(r"^ws/room/(?P<id>\d+)/$", RoomConsumer.as_asgi()),
        ]
    )
    return application

class _FakeLock:
    def __init__(self, lock: threading.Lock):
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._lock.release()

class FakeCache:
    def __init__(self):
        self._store: dict = {}
        self._locks: dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_lock(self, key: str) -> threading.Lock:
        with self._global_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]

    def lock(self, key: str):
        return _FakeLock(self._get_lock(key))

    def set(self, key: str, value, timeout=None):
        self._store[key] = value

    def get(self, key: str, default=None):
        return self._store.get(key, default)

    def get_many(self, keys):
        return {k: self._store[k] for k in keys if k in self._store}

    def delete(self, key: str):
        self._store.pop(key, None)

    def touch(self, key: str, timeout):
        return

    def flushall(self):
        self._store.clear()
        self._locks.clear()

@pytest.fixture
def fake_cache(monkeypatch):
    fake = FakeCache()

    import rooms.services.room_cache_service as room_cache_mod
    monkeypatch.setattr(room_cache_mod, "cache", fake)
    yield fake
    fake.flushall()
