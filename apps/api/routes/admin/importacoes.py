from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.database.session import get_session
from pydantic import BaseModel
import subprocess
import uuid

router = APIRouter(prefix="/v1/admin/importacoes", tags=["admin-importacoes"])


# GET - Lista importações
@router.get("")
async def listar_importacoes(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            distribuidora, 
            ano, 
            camada, 
            status, 
            data_execucao
        FROM plead.import_status
        ORDER BY data_execucao DESC
        LIMIT 100
    """)
    res = await db.execute(query)
    return [dict(r) for r in res.fetchall()]


# POST - Disparar importação
class ImportacaoPayload(BaseModel):
    distribuidora: str
    prefixo: str
    ano: int
    url: str
    camadas: list[str]  # Ex: ["UCAT", "UCMT", "UCBT"]

@router.post("/rodar")
async def rodar_importacao(payload: ImportacaoPayload):
    try:
        id_exec = str(uuid.uuid4())[:8]
        print(f"🚀 [{id_exec}] Disparando importação: {payload.prefixo} {payload.ano} camadas={payload.camadas}")

        # 1. Dispara o download
        subprocess.run([
            "python", "packages/jobs/downloads/download_gdb.py",
            "--distribuidora", payload.distribuidora,
            "--prefixo", payload.prefixo,
            "--ano", str(payload.ano),
            "--url", payload.url
        ], check=True)

        # 2. Dispara o orquestrador
        subprocess.run([
            "python", "packages/jobs/orquestrator/orquestrador.job.py",
            "--distribuidora", payload.distribuidora,
            "--ano", str(payload.ano),
            "--camadas", ",".join(payload.camadas),
            "--caminho_gdb", f"data/downloads/{payload.prefixo}_{payload.ano}.gdb"
        ], check=True)

        return {"status": "ok", "exec_id": id_exec}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao rodar importação: {str(e)}")
