import os
import sys
from pathlib import Path

import pytest

# Ensure project source is importable when tests are run from repo root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Код может быть собран либо как monorepo (apps/api/src), либо скопирован в /app/src внутри образа.
SRC_PATH = PROJECT_ROOT / "apps" / "api" / "src"
if not SRC_PATH.exists():
    SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Make sure pydantic picks up the local .env by default during tests
os.environ.setdefault("ENV_FILE", str(PROJECT_ROOT / ".env"))

from core.config import settings  # noqa: E402


@pytest.fixture(autouse=True)
def _override_settings(monkeypatch):
    """
    Keep tests hermetic by overriding secrets and volatile values.
    We only touch fields needed by pure-logic helpers under test.
    """
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "test-secret-key", raising=False)
    monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key", raising=False)
    monkeypatch.setattr(settings, "JWT_EXPIRES_MINUTES", 5, raising=False)
    monkeypatch.setattr(settings, "REFRESH_TOKEN_EXPIRES_DAYS", 1, raising=False)
    monkeypatch.setattr(settings, "APP_ENV", "test", raising=False)
    monkeypatch.setattr(settings, "DEBUG", True, raising=False)
    yield
