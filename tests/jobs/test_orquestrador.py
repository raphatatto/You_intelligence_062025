# tests/test_orquestrador.py

import pytest
from unittest import mock
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from packages.orquestrator.orquestrador_job import rodar_importer # ajuste se o nome do arquivo mudar

@pytest.fixture
def fake_gdbs(tmp_path):
    """
    Cria GDBs fictícios para teste.
    """
    gdbs = []
    nomes = ["CPFL_Paulista_2023", "ENEL_SP_2022"]
    for nome in nomes:
        gdb_path = tmp_path / f"{nome}.gdb"
        gdb_path.mkdir()
        gdbs.append(gdb_path)
    return gdbs

@mock.patch("packages.jobs.orquestrator.orquestrador.DOWNLOADS_DIR", new_callable=lambda: Path("tests/fake_gdb"))
@mock.patch("packages.jobs.orquestrator.orquestrador.run")
@mock.patch("packages.jobs.orquestrator.orquestrador.get_status", return_value="not_started")
def test_orquestrador_roda_todas_camadas(mock_status, mock_run, mock_downloads_dir, tmp_path, monkeypatch):
    # Setup: simula gdbs
    monkeypatch.setattr("packages.jobs.orquestrator.orquestrador.DOWNLOADS_DIR", tmp_path)
    (tmp_path / "CPFL_Paulista_2023.gdb").mkdir()
    (tmp_path / "ENEL_SP_2022.gdb").mkdir()

    # Executa
    rodar_importer.main()

    # Valida se subprocess.run foi chamado para cada camada por prefixo
    expected_calls = 3 * 2  # 3 camadas * 2 GDBs
    assert mock_run.call_count == expected_calls

    comandos_executados = [call.args[0] for call in mock_run.call_args_list]

    for cmd in comandos_executados:
        assert isinstance(cmd, list)
        assert any(cam in cmd for cam in ["UCAT", "UCMT", "UCBT"])
        assert any(p in cmd for p in ["CPFL_Paulista_2023", "ENEL_SP_2022"])
