# Documentação Atualizada do Schema `intel_lead`

**Última atualização:** 2025-07-11

---

## 📊 Visão Geral

O schema `intel_lead` é o coração da plataforma Youon Intelligence. Ele foi projetado para ingestão, enriquecimento, análise e exposição de dados de unidades consumidoras (UCs) do setor elétrico. O modelo permite ingestão massiva de dados abertos da ANEEL, armazenamento eficiente por camadas (UCAT, UCMT, UCBT), e enriquecimento com coordenadas, CNPJ e dados externos.

### Componentes

1. **Tabelas base:** `lead_bruto`, `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal`
2. **Domínios e enums:** distribuidora, grupos, classes, enums de status
3. **Controle e logging:** `import_status`, `lead_enrichment_log`
4. **Views (API-ready):** views operacionais, enriquecidas e analíticas
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

* `classe_consumo`, `grupo_tensao`, `modalidade_tarifaria`, `tipo_sistema`, `situacao_uc`: usados para normalização do lead
* `segmento_mercado`: segmentação setorial estimada via CNAE
* `distribuidora`: mapeamento das concessionárias
* `municipio`: base geográfica (nome + UF)
* `cnae`: classificação nacional de atividade econômica
* `ponto_notavel`: coordenadas conhecidas (usado como fallback)

---

## 📊 Tabelas Principais

### `lead_bruto`

Armazena metadados principais da UC.

### `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal`

Tabelas de séries temporais com dados técnicos mensais. Relacionam-se via `uc_id`.

### `import_status` e `lead_enrichment_log`

Controle de ingestão e enriquecimento (log de execuções).

### `ponto_notavel`

Fallback de localização para UCs sem coordenadas.

---

## 🔎 Views Operacionais e Enriquecidas

### `lead_com_coordenadas`

Adiciona latitude/longitude final com fallback.

### `vw_lead_com_cnae_desc`

Estende com descrição CNAE, segmento e localização.

### `vw_lead_status_enriquecimento`

Último status de enriquecimento por `lead_bruto_id`.

### `vw_lead_energia_agg`

Média e soma de energia (ponta, fora ponta, total) por lead.

### `vw_lead_demanda_agg`

Média e soma de demanda (ponta, fora ponta, contratada, total).

### `vw_lead_qualidade_agg`

Média de DIC, FIC e total de horas sem rede por lead.

### `vw_lead_completo_detalhado`

> View principal que consolida todos os dados técnicos, normalizados, geográficos e enriquecidos de um lead.

Inclui:

* Dados brutos do lead
* Fallback de coordenadas
* Domínios normalizados
* CNAE + Segmento
* Enriquecimento atual
* Agregados de energia, demanda e qualidade

Usada como base para painel admin, dashboards e API REST.

---

## ✨ Views Materializadas (Resumo/Admin/API)

### `resumo_energia_municipio`, `resumo_leads_distribuidora`, `resumo_leads_ano_camada`

Materialized views para análises rápidas. Devem ser atualizadas com `REFRESH MATERIALIZED VIEW nome`.

---

## ⚖️ Indexação e Desempenho

* Índices por UC, distribuidora, importação
* Aceleração de joins com domínios e series temporais

---

## 🧪 Queries Reais

* Leads com enriquecimento completo e PAC elevado:

```sql
SELECT * FROM vw_lead_completo_detalhado
WHERE enriquecimento_status = 'success' AND pac > 15000;
```

* Leads com DIC/FIC acima da média:

```sql
SELECT * FROM vw_lead_completo_detalhado
WHERE media_dic > 10 OR media_fic > 15;
```

---

## 🛡️ Proteção de Tabelas Críticas

As tabelas `cnae`, `municipio`, `grupo_tensao`, etc., estão protegidas contra alterações acidentais por triggers com exceção explícita. Remoção possível via `DROP TRIGGER`.

---

## 📘 Integração com API

Views como `vw_lead_completo_detalhado`, `vw_lead_status_enriquecimento`, `resumo_leads_distribuidora` são recomendadas para uso direto na API REST ou interfaces como o painel administrativo.

---

## 📌 Glossário

| Termo         | Definição                                |
| ------------- | ---------------------------------------- |
| UC            | Unidade Consumidora                      |
| PAC           | Potência Ativa Contratada                |
| DIC/FIC       | Indicadores de qualidade elétrica        |
| CNAE          | Classificação Nacional de Atividades     |
| Ponto Notável | Coordenada auxiliar de fallback          |
| Camada        | Fonte dos dados ANEEL (UCAT, UCMT, etc.) |

---

Documentação oficial. Versão atual: `v1.4.0`
