import os, sys, json, shutil, tempfile, pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def temp_data_dir(monkeypatch):
    tmpdir = Path(tempfile.mkdtemp())
    data_dir = tmpdir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for name in ["appointments.json", "patients.json", "invoices.json", "plans.json", "users.json"]:
        (data_dir / name).write_text("[]", encoding="utf-8")

    old_cwd = Path.cwd()
    monkeypatch.chdir(data_dir)

    try:
        yield data_dir
    finally:
        monkeypatch.chdir(old_cwd)
        shutil.rmtree(tmpdir, ignore_errors=True)
