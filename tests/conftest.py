import os
import tempfile

# Vale já na importação dos módulos de teste (antes das fixtures)
os.environ["SECOPS_SRC_DB_PATH"] = os.path.join(
    tempfile.mkdtemp(prefix="secops_tests_"), "session.db"
)

import pytest  # noqa: E402
from src.core.database import init_db  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_src_db(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOPS_SRC_DB_PATH", str(tmp_path / "test.db"))
    init_db()