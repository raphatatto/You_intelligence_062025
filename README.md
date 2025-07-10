# ⚡ Youon Intelligence – Plataforma de Inteligência de Mercado no Setor de Energia

Bem-vindo ao repositório oficial do **Youon Intelligence**, uma solução robusta de ingestão, enriquecimento e análise de dados energéticos em larga escala. A plataforma transforma dados brutos da ANEEL e outras fontes públicas em inteligência estratégica para áreas técnicas, comerciais e executivas da You.On.

---

## 💡 Visão Geral

Este projeto processa **milhões de registros** vindos de diferentes fontes (ANEEL, CCEE, Receita Federal, etc.) para produzir:

* Leads qualificados para os produtos Arbitragem, Backup, GTD, etc.
* Insights geoespaciais e temporais do consumo e demanda elétrica
* Indicadores de qualidade por município, cliente e distribuidora
* Dashboards administrativos e API pública de consulta

---

## 📌 Funcionalidades

* 🔄 Importação automatizada de arquivos UCAT, UCMT, UCBT (GDB ou CSV)
* 🧹 Normalização e transformação de dados para estrutura relacional
* 🧠 Enriquecimento com APIs externas: CNPJ, CNAE, coordenadas
* 📊 Visualização por mapas, séries temporais e agregações
* 🔍 Pipeline auditável com versionamento e controle de status
* 🧰 Indexação, views otimizadas e materialized views com refresh

---

## 🛠️ Stack Tecnológica

| Camada         | Tecnologia                             |
| -------------- | -------------------------------------- |
| Backend        | Python 3.11, FastAPI                   |
| Frontend       | Next.js (React), Tailwind CSS          |
| Banco de Dados | PostgreSQL (Azure) com extensões GIS   |
| Jobs & ETL     | Pandas, GeoPandas, psycopg2, Fiona     |
| Orquestração   | Apache Airflow                         |
| IA / ML        | Scikit-learn, HuggingFace Transformers |
| Deploy         | Docker, Docker Compose, Terraform      |

---

## 📂 Estrutura de Pastas (Escalável e Modular)

```bash
youon-intelligence/
├── apps/
│   ├── api/                # FastAPI backend
│   └── frontend/           # Next.js + Tailwind
├── packages/
│   ├── jobs/               # ETL (importers, enrichers, transformers)
│   ├── ai/                 # Treinamento, modelos e inferência
│   ├── database/           # Schema, conexão, índices
│   └── orchestrator/       # DAGs do Airflow
├── infra/                  # Docker, Terraform, scripts
├── data/                   # Arquivos CSV, GDB, logs e modelos
├── tests/                  # Pytest para API, jobs e AI
├── docs/                   # Diagramas, glossário, dataset map
├── requirements.txt
├── .env.example
├── Makefile
└── README.md
```

---

## 🧱 Estrutura de Banco – Schema `intel_lead`

As principais tabelas incluem:

* `lead_bruto` – unidade consumidora base com metadados técnicos
* `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal` – séries temporais mensais
* `import_status` – rastreio de ingesão (camada, distribuidora, ano, status)
* `lead_enrichment_log` – status e etapas de enriquecimento
* Tabelas de domínio (classe, modalidade, grupo tensão, etc.)

### 📍 Views e Materialized Views

* `lead_com_coordenadas` – junta UC + ponto notável
* `resumo_energia_municipio`, `resumo_leads_distribuidora`, `resumo_leads_ano_camada` – materializadas com `REFRESH`
* `vw_lead_status_enriquecimento`, `vw_import_status_resumido`, `vw_lead_com_cnae_desc` – para API/admin

---

## 🧆 Dataset Técnicos Usados

* [BDGD ANEEL (Geo)](https://dadosabertos-aneel.opendata.arcgis.com/)
* [ANEEL CSV (UCAT, UCMT, UCBT)](https://dadosabertos.aneel.gov.br/)
* Receita Federal (CNPJá API)
* Google Maps API, OpenWeather, IBGE
* ENEL EQME, EQSE, UCAT\_tab, etc.

---

## 🚀 Primeiros Passos (Dev)

1. Clone o repositório:

   ```bash
   git clone https://github.com/youon/youon-intelligence.git
   cd youon-intelligence
   ```

2. Instale os requisitos:

   ```bash
   pip install -r requirements.txt
   ```

3. Copie e edite seu `.env`:

   ```bash
   cp .env.example .env
   ```

4. Execute a API:

   ```bash
   uvicorn apps.api.main:app --reload
   ```

5. Execute um job (exemplo):

   ```bash
   python packages/jobs/importers/importer_ucat_job.py
   ```

---

## 🧪 Testes Automatizados

* Testes com `pytest`, cobertura com `coverage`
* Jobs, API e AI validados em `tests/`

---

## 📆 Deploy e Orquestração

* `docker-compose up --build`
* Orquestração com Airflow: `packages/orchestrator/`
* Infraestrutura com Terraform (Azure)

---

## 🔐 Segurança

* Autenticação com JWT
* Acesso administrativo restrito por IP/VPN

---

## 👥 Contribuidores

* Guilherme Costa Proença – Engenharia de Software e Dados
* \[@SeuGithub] – Backend/ML
* \[@Colaborador] – Frontend/DevOps

---

## 🔬 Próximas Etapas

* Clusterização geográfica de UCs
* Sistema de recomendação de solução (GTD, Arbitragem…)
* Automação da análise de qualidade (DIC/FIC) com ML

---

> “Não adianta ter os dados. O valor está em transformá-los em inteligência.” – YouOn Tech Team
