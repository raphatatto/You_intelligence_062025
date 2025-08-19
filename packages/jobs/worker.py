# packages/jobs/worker.py
# -*- coding: utf-8 -*-
"""
Worker de importação:
- Consome jobs da tabela import_queue (packages/jobs/queue.py)
- Opcionalmente baixa o GDB (com retomada/limite de banda) antes do import
- Executa o importer em processo filho com prioridade baixa (nice/ionice/psutil)
- Reenfileira com backoff em falha, finaliza como done em sucesso
"""

import os
import shlex
import subprocess
import time
import uuid
from typing import Dict, Any, Optional

from packages.jobs.queue import dequeue, complete, fail, WORKER_POLL_SEC

# download helper
try:
    from packages.jobs.download_gdb import baixar_gdb
except Exception:
    baixar_gdb = None  # opcional

NICE_BIN = os.getenv("NICE_BIN", "nice")
IONICE_BIN = os.getenv("IONICE_BIN", "ionice")
USE_IONICE = os.getenv("USE_IONICE", "1") == "1"

def _set_low_priority_psutil(proc: subprocess.Popen) -> None:
    try:
        import psutil, platform
        p = psutil.Process(proc.pid)
        if platform.system() == "Windows":
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(15)
    except Exception:
        pass

def _spawn_low_priority(cmd: list[str], env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
    # POSIX: tenta ionice + nice; Windows: apenas chama e reduz via psutil
    try:
        import platform
        if platform.system() != "Windows":
            wrapped = [NICE_BIN, "-n", "15"]
            if USE_IONICE:
                wrapped = [IONICE_BIN, "-c2", "-n", "7"] + wrapped
            wrapped = wrapped + cmd
            proc = subprocess.Popen(wrapped, env=env)
        else:
            proc = subprocess.Popen(cmd, env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        _set_low_priority_psutil(proc)
        return proc
    except FileNotFoundError:
        # sem nice/ionice no sistema
        return subprocess.Popen(cmd, env=env)

def _build_cmd(payload: Dict[str, Any]) -> list[str]:
    script = payload["script"]                      # ex: packages/jobs/importers/importer_ucbt_job.py
    args = [str(a) for a in (payload.get("args") or [])]
    pybin = os.getenv("PYTHON_BIN", "python")
    return [pybin, script] + args

def _maybe_download(download_spec: Dict[str, Any]) -> Optional[str]:
    """
    Executa download se 'download' veio no payload.
    Espera chaves: distribuidora, ano, nome_destino (opcional), url (opcional), max_kbps (opcional)
    Retorna caminho da pasta .gdb final ou None.
    """
    if baixar_gdb is None or not download_spec:
        return None
    dist = download_spec.get("distribuidora")
    ano = int(download_spec.get("ano"))
    url = download_spec.get("url")  # se não vier, a função interna pode resolver
    nome_destino = download_spec.get("nome_destino")  # ex: ENEL_RJ_2023
    max_kbps = int(download_spec.get("max_kbps") or 256)
    return str(baixar_gdb(distribuidora=dist, ano=ano, url=url, nome_destino=nome_destino, max_kbps=max_kbps))

def main():
    worker_id = f"worker-{uuid.uuid4().hex[:8]}"
    print(f"[worker] started: {worker_id}")

    while True:
        job = dequeue(worker_id)
        if not job:
            time.sleep(WORKER_POLL_SEC)
            continue

        job_id = job["id"]
        payload: Dict[str, Any] = job["payload"]
        tries = job.get("tries", 0)
        max_retries = job.get("max_retries", 3)

        # ambiente do processo filho
        env = os.environ.copy()
        for k, v in (payload.get("env") or {}).items():
            env[str(k)] = str(v)

        try:
            # 1) download opcional (retomável/limitado)
            if payload.get("download"):
                gdb_path = _maybe_download(payload["download"])
                # opcional: substituir placeholder --gdb=<auto>
                if gdb_path:
                    args = payload.get("args") or []
                    for i, a in enumerate(args):
                        if a == "--gdb" and i + 1 < len(args):
                            args[i + 1] = gdb_path
                    payload["args"] = args

            # 2) executar importer
            cmd = _build_cmd(payload)
            print(f"[worker] running job {job_id}: {shlex.join(cmd)}")
            proc = _spawn_low_priority(cmd, env=env)
            ret = proc.wait()

            if ret == 0:
                print(f"[worker] job {job_id} done")
                complete(job_id)
            else:
                print(f"[worker] job {job_id} failed (exit={ret})")
                fail(job_id, delay_sec=min(60 * (tries + 1), 600))  # backoff

        except Exception as e:
            print(f"[worker] exception on job {job_id}: {e}")
            fail(job_id, delay_sec=min(60 * (tries + 1), 600))

if __name__ == "__main__":
    main()
