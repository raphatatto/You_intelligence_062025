# Intel Lead Schema Documentation

Este documento reúne toda a documentação do schema `intel_lead`, incluindo visão geral, dicionário de dados, diagrama ER, exemplos de queries, processo de deploy/migração, política de retenção e glossário de termos de negócio.

---

## 1. Visão Geral

O schema `intel_lead` foi projetado para suportar análise geoespacial e temporal de unidades consumidoras (UC) no setor de energia, integrando dados de:

* **Importações** (controle de cargas)
* **Dados brutos** de UCs
* **Séries temporais** mensais (energia, demanda, qualidade de serviço)
* **Pontos notáveis** de infraestrutura
* **Logs** de enriquecimento (geocoding, validações externas)
* **Agregações** em views e materialized views para relatórios rápidos

### Componentes

1. **Enums** — `camada_enum`, `status_enum`, `origem_enum`, `resultado_enum`.
2. **Lookup Tables** — domínios de tensão, tarifa, sistema, classe, situação, segmento, distribuidoras, municípios.
3. **Tabelas de Controle** — `import_status`.
4. **Dados Principais** — `lead_bruto`.
5. **Séries Temporais** — `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal`.
6. **Logging** — `lead_enrichment_log`.
7. **Infraestrutura** — `ponto_notavel`.
8. **Views** — `lead_com_coordenadas` e `resumo_energia_por_municipio`.

---

## 2. Dicionário de Dados Detalhado

### Tabela `lead_bruto`

| Coluna            | Tipo             | Descrição                                 | Restrição                       |
| ----------------- | ---------------- | ----------------------------------------- | ------------------------------- |
| id                | UUID             | Identificador único da linha              | PK, DEFAULT gen\_random\_uuid() |
| uc\_id            | TEXT             | Identificador lógico da UC                | INDEX (não-único)               |
| import\_id        | TEXT             | Referência à importação                   | FK → import\_status(import\_id) |
| cod\_id           | TEXT             | Código interno da UC                      | NOT NULL                        |
| distribuidora\_id | INT              | Distribuidora responsável                 | FK → distribuidora(id)          |
| origem            | origem\_enum     | Origem da UC (UCAT, UCMT, UCBT)           | NOT NULL                        |
| ano               | INT              | Ano de referência                         | NOT NULL                        |
| status            | TEXT             | Status interno (`raw`, `processed`, etc.) | DEFAULT 'raw'                   |
| data\_conexao     | DATE             | Data de conexão da UC                     |                                 |
| cnae              | INT              | Código CNAE                               |                                 |
| grupo\_tensao     | TEXT             | Grupo de tensão                           | FK → grupo\_tensao(id)          |
| modalidade        | TEXT             | Modalidade tarifária                      | FK → modalidade\_tarifaria(id)  |
| tipo\_sistema     | TEXT             | Tipo de sistema                           | FK → tipo\_sistema(id)          |
| situacao          | TEXT             | Situação da UC                            | FK → situacao\_uc(id)           |
| classe            | TEXT             | Classe de consumo                         | FK → classe\_consumo(id)        |
| segmento          | TEXT             | Segmento de mercado                       | FK → segmento\_mercado(id)      |
| subestacao        | TEXT             | Subestação da UC                          |                                 |
| municipio\_id     | INT              | Código do município                       | FK → municipio(id)              |
| bairro            | TEXT             | Bairro                                    |                                 |
| cep               | TEXT             | CEP da unidade                            |                                 |
| pac               | INT              | Potência ativa contratada                 |                                 |
| pn\_con           | TEXT             | Ponto notável                             |                                 |
| descricao         | TEXT             | Observações gerais                        |                                 |
| latitude          | DOUBLE PRECISION | Latitude                                  |                                 |
| longitude         | DOUBLE PRECISION | Longitude                                 |                                 |
| created\_at       | TIMESTAMP        | Timestamp de criação                      | DEFAULT CURRENT\_TIMESTAMP      |
| updated\_at       | TIMESTAMP        | Timestamp de atualização                  | DEFAULT CURRENT\_TIMESTAMP      |

### Tabelas `lead_energia_mensal`, `lead_demanda_mensal`, `lead_qualidade_mensal`

As três compartilham estrutura similar. Destaque para:

| Coluna               | Tipo             | Descrição                         | Restrição                       |
| -------------------- | ---------------- | --------------------------------- | ------------------------------- |
| id                   | UUID             | Identificador único               | PK                              |
| lead\_bruto\_id      | UUID             | Referência à linha de lead\_bruto | FK → lead\_bruto(id)            |
| mes                  | INT              | Mês (1–12)                        | CHECK                           |
| origem               | origem\_enum     | Origem da informação              | NOT NULL                        |
| energia\_ponta       | DOUBLE PRECISION | Energia em horário de ponta (MWh) | (energia\_mensal apenas)        |
| energia\_fora\_ponta | DOUBLE PRECISION | Energia fora de ponta (MWh)       |                                 |
| demanda\_total       | DOUBLE PRECISION | Demanda total (kW)                | (demanda\_mensal apenas)        |
| dic, fic, sremede    | DOUBLE PRECISION | Indicadores de qualidade          | (qualidade\_mensal apenas)      |
| import\_id           | TEXT             | Referência à importação           | FK → import\_status(import\_id) |

### Tabela `lead_enrichment_log`

| Coluna          | Tipo            | Descrição                            | Restrição                  |
| --------------- | --------------- | ------------------------------------ | -------------------------- |
| id              | UUID            | Identificador único                  | PK                         |
| lead\_bruto\_id | UUID            | FK para lead\_bruto                  | FK → lead\_bruto(id)       |
| etapa           | TEXT            | Etapa do enriquecimento              |                            |
| resultado       | resultado\_enum | Resultado (success, failed, partial) |                            |
| detalhes        | TEXT            | Logs ou JSON da execução             |                            |
| executado\_em   | TIMESTAMP       | Data/hora do enriquecimento          | DEFAULT CURRENT\_TIMESTAMP |

### Tabela `ponto_notavel`

| Coluna    | Tipo             | Descrição              | Restrição |
| --------- | ---------------- | ---------------------- | --------- |
| pn\_id    | TEXT             | Identificador do ponto | PK        |
| latitude  | DOUBLE PRECISION | Latitude geográfica    |           |
| longitude | DOUBLE PRECISION | Longitude geográfica   |           |

---

## 3. Diagrama ER

Você pode usar DBeaver, pgModeler ou outro para gerar o ERD. O diagrama deve:

* Destacar `lead_bruto.id` como PK real
* Mostrar FKs `lead_bruto_id` nas tabelas filhas
* Exibir joins com `distribuidora`, `municipio`, `grupo_tensao`, etc.

---

## 4. Exemplos de Queries Comuns

```sql
-- 1) Leads sem coordenadas definidas:
SELECT id, cod_id
FROM lead_bruto
WHERE latitude IS NULL AND longitude IS NULL;

-- 2) Energia total por distribuidora/ano:
SELECT l.distribuidora_id, l.ano, SUM(e.energia_total) AS energia
FROM lead_bruto l
JOIN lead_energia_mensal e ON l.id = e.lead_bruto_id
GROUP BY l.distribuidora_id, l.ano;

-- 3) Imports que falharam:
SELECT *
FROM import_status
WHERE status = 'failed';

-- 4) Atualizar view materializada:
REFRESH MATERIALIZED VIEW resumo_energia_por_municipio;
```

---

## 5. Deploy e Migração

* Adote Flyway ou Liquibase para versionar alterações de schema.
* Organize scripts em pastas `V1__create_schema.sql`, `V2__add_column.sql`, etc.
* No CI/CD, inclua etapa de migração antes dos testes.
* Controle permissões: roles `data_ingest`, `data_read`, `data_admin`.

---

## 6. Política de Retenção e Particionamento

* Particione tabelas mensais (`lead_energia_mensal`, etc.) por `ano` ou `created_at`.
* Exemplo com declarative partitioning (Postgres 12+):

```sql
CREATE TABLE lead_energia_mensal_2025 PARTITION OF lead_energia_mensal FOR VALUES IN (2025);
```

* Defina políticas de retenção conforme LGPD e necessidade do projeto.

---

## 7. Glossário de Termos de Negócio

| Sigla   | Significado                                                   |
| ------- | ------------------------------------------------------------- |
| UC      | Unidade Consumidora                                           |
| PN      | Ponto Notável                                                 |
| PAC     | Potência Ativa Contratada                                     |
| CNAE    | Classificação Nacional de Atividades Econômicas               |
| DEC/FEC | Indicadores de Continuidade de Energia (Duração e Frequência) |
| ACL/ACR | Ambiente de Contratação Livre/Cativo                          |
| PLD     | Preço de Liquidação das Diferenças                            |

---

*Documentação atualizada em: 2025-07-08*
