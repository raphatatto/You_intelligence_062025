import subprocess

def run_job(nome, path):
    print(f"\n🔹 Executando: {nome}")
    result = subprocess.run(["python", path])
    if result.returncode == 0:
        print(f"✅ {nome} finalizado com sucesso.")
    else:
        print(f"❌ Erro ao rodar {nome}.")

if __name__ == "__main__":
    print("📊 Iniciando orquestração do pipeline de enriquecimento...\n")

    steps = [
        ("Priorizar Leads", "packages/jobs/classificadores/priorizador_enriquecimento_job.py"),
        ("Mover Leads Desativados", "packages/jobs/classificadores/mover_leads_inuteis_job.py")
    ]

    for nome, path in steps:
        run_job(nome, path)

    print("\n🏁 Pipeline de enriquecimento executado.")
