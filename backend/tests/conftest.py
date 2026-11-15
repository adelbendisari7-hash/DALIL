import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DALIL_DATABASE_URL"] = f"sqlite:///{_tmp.as_posix()}"
os.environ["DALIL_ADMIN_PHONES"] = "0550000099"
os.environ["DALIL_DIAGNOSIS_RATE_PER_MINUTE"] = "1000"
os.environ["DALIL_OTP_RATE_PER_MINUTE"] = "1000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.security import ConsoleSms  # noqa: E402
from app.seed import run as seed_run  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_run(db, demo=True)
    yield


@pytest.fixture()
def db():
    with SessionLocal() as s:
        yield s


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def login(client: TestClient, phone: str) -> dict:
    r = client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert r.status_code == 200, r.text
    norm = r.json()["phone"]
    code = ConsoleSms.last[norm].split()[-1]
    r = client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": code})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="session")
def admin_headers(client):
    return login(client, "0550000099")
