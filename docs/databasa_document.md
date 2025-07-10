# Documentação Atualizada do Schema `intel_lead`

**Última atualização:** 2025-07-10

---

## 📊 Visão Geral

O schema `intel_lead` é o coração da plataforma Youon Intelligence. Ele foi projetado para ingestão, enriquecimento, análise e exposição de dados de unidades consumidoras (UCs) do setor elétrico. O modelo permite ingestão massiva de dados abertos da ANEEL, armazenamento eficiente por camadas (UCAT, UCMT, UCBT), e enriquecimento com coordenadas, CNPJ e dados externos.

### Componentes

1. **Tabelas base:** `lead_bruto`, `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal`
2. **Domínios e enums:** distribuidora, grupos, classes, enums de status
3. **Controle e logging:** `import_status`, `lead_enrichment_log`
4. **Views (API-ready):** views operacionais e de dashboard
5. **Materialized views:** sumarizações para leitura rápida no admin/API
6. **Extensões de localização:** `ponto_notavel`, `lead_com_coordenadas`

---

## 📑 Enumerações e Domínios

```sql
CREATE TYPE camada_enum AS ENUM ('UCAT', 'UCMT', 'UCBT', 'PONNOT');
CREATE TYPE status_enum AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE origem_enum AS ENUM ('UCAT', 'UCMT', 'UCBT');
CREATE TYPE resultado_enum AS ENUM ('success', 'partial', 'failed');
```

As tabelas de domínio (ex: `modalidade_tarifaria`, `tipo_sistema`) possuem `id` (text) e `descricao`, e são usadas como FK no `lead_bruto`.

### Tabelas de Domínio

* `classe_consumo`: classificação da UC em função de sua natureza (comercial, residencial, industrial, etc.) e tipo de cliente (`PF`, `PJ`)
* `grupo_tensao`: grupo de fornecimento de tensão elétrica (alta, baixa, etc.)
* `modalidade_tarifaria`: tipo de tarifação aplicada à UC (convencional, branca, horo-sazonal, etc.)
* `tipo_sistema`: identifica se a unidade é trifásica, bifásica ou monofásica
* `situacao_uc`: situação da UC junto à distribuidora (ativa, cortada, desligada, etc.)
* `segmento_mercado`: estimativa de segmento com base em CNAE
* `distribuidora`: entidades concessionárias mapeadas por código ANEEL
* `municipio`: base de municípios com UF, usada para junções e agregações
* `cnae`: código e descrição da Classificação Nacional de Atividades Econômicas
* `ponto_notavel`: coordenadas conhecidas (subestações, transformadores, torres, etc.)

---

## 📊 Tabelas Principais

### `lead_bruto`

Armazena metadados principais de cada UC por import. PK: `uc_id`

* Identificação e import: `uc_id`, `cod_id`, `import_id`, `ano`, `origem`, `status`
* Localização: `municipio_id`, `bairro`, `cep`, `pn_con`, `latitude`, `longitude`
* Características: `modalidade`, `grupo_tensao`, `tipo_sistema`, `classe`, `segmento`, `subestacao`, `situacao`, `pac`, `descricao`, `cnae`
* Indexação: `idx_lead_distribuidora_ano`, `idx_lead_pncon`, `idx_lead_uc_id`

### `lead_energia_mensal`

Energia ativa (MWh) mensal. PK composta: `(uc_id, mes)`

* Colunas: `energia_ponta`, `energia_fora_ponta`, `energia_total`, `origem`, `import_id`

### `lead_demanda_mensal`

Demanda (kW) mensal por UC. Colunas: `demanda_ponta`, `fora_ponta`, `contratada`, `total`, `origem`, `import_id`

### `lead_qualidade_mensal`

Indicadores DIC/FIC/SemRede mensais por UC. PK composta: `(uc_id, mes)`

### `import_status`

Controle de execução das importações. PK: `import_id`

* Contém status (`pending`, `completed`, `failed`), datas de início/fim, camada e quantidade de linhas processadas

### `lead_enrichment_log`

Log de execução de jobs de enriquecimento (geolocalização, CNPJ, etc). Relacionado via `uc_id`

* Campos: `etapa`, `resultado`, `executado_em`, `detalhes`

### `ponto_notavel`

Coordenadas conhecidas de subestações, transformadores, etc. Pode ser associado a UC via `pn_con`

---

## 🔎 Views Operacionais

### `lead_com_coordenadas`

View que resolve coordenadas finais da UC com fallback para `ponto_notavel`

```sql
SELECT
  l.*,
  COALESCE(l.latitude, p.latitude)  AS latitude_final,
  COALESCE(l.longitude, p.longitude) AS longitude_final
FROM lead_bruto l
LEFT JOIN ponto_notavel p ON l.pn_con = p.pn_id;
```

### `vw_lead_com_cnae_desc`

Extensão da view acima com dados de CNAE, localização final, setor e descritores

### `vw_lead_status_enriquecimento`

Status da etapa mais recente de enriquecimento para cada UC (por `uc_id`) com `resultado`, `executado_em`

### `vw_import_status_resumido`

Resumo agregador de import status por `ano`, `camada`, `status`, `linhas_processadas`

### `vw_dashboard_status_leads`

Indicadores de total por status (`raw`, `enriched`, `partially_enriched`, `failed`) por distribuidora

---

## ✨ Views Materializadas (Resumo/Admin/API)

As views a seguir devem ser atualizadas manualmente ou via cron agendado.

### `resumo_energia_municipio`

Energia total (MWh) por município:

```sql
CREATE MATERIALIZED VIEW resumo_energia_municipio AS
SELECT
  m.id   AS municipio_id,
  m.nome,
  m.uf,
  SUM(e.energia_total)     AS energia_total,
  COUNT(DISTINCT l.uc_id)  AS total_leads
FROM lead_bruto l
JOIN municipio m           ON l.municipio_id = m.id
JOIN lead_energia_mensal e ON l.uc_id = e.uc_id
GROUP BY m.id, m.nome, m.uf;
```

### `resumo_leads_distribuidora`

```sql
CREATE MATERIALIZED VIEW resumo_leads_distribuidora AS
SELECT
  d.id,
  d.nome_comum,
  COUNT(*)                      AS total_imports,
  COUNT(DISTINCT l.uc_id)      AS total_leads,
  COUNT(DISTINCT e.uc_id)      AS leads_com_energia,
  COUNT(DISTINCT q.uc_id)      AS leads_com_qualidade
FROM distribuidora d
LEFT JOIN lead_bruto l     ON d.id = l.distribuidora_id
LEFT JOIN lead_energia_mensal e ON l.uc_id = e.uc_id
LEFT JOIN lead_qualidade_mensal q ON l.uc_id = q.uc_id
GROUP BY d.id, d.nome_comum;
```

### `resumo_leads_ano_camada`

```sql
CREATE MATERIALIZED VIEW resumo_leads_ano_camada AS
SELECT
  ano,
  origem::TEXT AS camada,
  COUNT(*) AS total_leads
FROM lead_bruto
GROUP BY ano, origem;
```

#### ⚠️ Importante:

Para atualizar todas:

```sql
REFRESH MATERIALIZED VIEW resumo_energia_municipio;
REFRESH MATERIALIZED VIEW resumo_leads_distribuidora;
REFRESH MATERIALIZED VIEW resumo_leads_ano_camada;
```

---

## ⚖️ Estratégias de Indexação

* `idx_lead_distribuidora_ano`: otimiza buscas por ano e distribuidora
* `idx_lead_pncon`: resolve geolocalização
* `idx_import_status_combo`: acelera queries agregadas por camada/ano
* `idx_lead_uc_id`: acesso rápido para joins nas mensais
* `idx_lead_status`: filtro por `status` na pipeline
* Índices auxiliares: `idx_energia_mes`, `idx_qualidade_lead_id`, `idx_demanda_lead_id`

---

## 🧪 Exemplos de Queries Realistas

* Leads PJ com PAC alto e sem consumo:

```sql
SELECT *
FROM lead_bruto
WHERE classe = 'PJ' AND pac > 10000 AND uc_id NOT IN (SELECT uc_id FROM lead_energia_mensal);
```

* UCs com enriquecimento com falha:

```sql
SELECT *
FROM lead_enrichment_log
WHERE resultado = 'failed';
```

* Energia média por UF e classe:

```sql
SELECT m.uf, lb.classe, AVG(em.energia_total)
FROM lead_bruto lb
JOIN municipio m ON lb.municipio_id = m.id
JOIN lead_energia_mensal em ON lb.uc_id = em.uc_id
GROUP BY m.uf, lb.classe;
```

---

## 🗃️ Política de Particionamento (futuro)

As tabelas `*_mensal` podem ser otimizadas com:

```sql
CREATE TABLE lead_energia_mensal_2025 PARTITION OF lead_energia_mensal FOR VALUES IN (2025);
```

Isso facilita manutenção, limpeza e performance.

---

## 📄 Documentação Interna e Comentários

Todas as tabelas, views, índices e colunas principais já estão com `COMMENT ON` aplicados via DBeaver.
Verifique a guia "Propriedades" para explicação em cada estrutura.

---

## 🧩 Relacionamentos Entre Tabelas

* `lead_bruto.uc_id` → chave principal do schema, conecta com todas as tabelas mensais
* `lead_bruto.import_id` → controla a origem dos dados (UCAT, UCMT, etc.)
* `lead_bruto.pn_con` → opcional, para fallback de coordenadas via `ponto_notavel`
* `lead_bruto.cnae` → relacionável com `cnae.codigo`
* `lead_bruto.municipio_id` → FK para `municipio`
* `lead_bruto.classe`, `modalidade`, etc. → relacionamentos com tabelas de domínio

---

## 🌐 Glossário Rápido

| Termo         | Definição                                                                  |
| ------------- | -------------------------------------------------------------------------- |
| UC            | Unidade Consumidora                                                        |
| PAC           | Potência Ativa Contratada                                                  |
| DIC/FIC       | Indicadores de qualidade de serviço elétrico (duração/frequência de falta) |
| CNAE          | Código Nacional de Atividades Econômicas                                   |
| Ponto Notável | Coordenada usada como fallback para geolocalização da UC                   |
| Camada        | Nome lógico de origem da base (UCAT, UCMT, UCBT)                           |

---

## 📘 Recomendado: Integração com API

As views `vw_lead_completo`, `vw_lead_status_enriquecimento`, `resumo_leads_distribuidora` estão prontas para uso direto na API.

* Exponha via endpoint `/v1/admin/dashboard/resumo`
* Use SWR/React para `refresh` automático das materialized views com indicação de tempo

---

Qualquer modificação de estrutura deve ser documentada nesta base.
Para sugestões, seguir padrão SemVer no versionamento da estrutura: `v1.2.0` etc.
