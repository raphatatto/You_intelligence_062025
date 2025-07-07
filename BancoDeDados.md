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

| Tabela                    | Coluna                                              | Tipo             | Descrição                                 | Restrição                       |
| ------------------------- | --------------------------------------------------- | ---------------- | ----------------------------------------- | ------------------------------- |
| **import\_status**        | import\_id                                          | TEXT             | Identificador único da importação         | PK                              |
|                           | distribuidora\_id                                   | INT              | Código da distribuidora                   | FK → distribuidora(id)          |
|                           | ano                                                 | INT              | Ano da importação                         | NOT NULL                        |
|                           | camada                                              | camada\_enum     | Camada de origem dos dados                | NOT NULL                        |
|                           | status                                              | status\_enum     | Status do processo de importação          | NOT NULL                        |
|                           | linhas\_processadas                                 | INT              | Número de linhas processadas              |                                 |
|                           | data\_inicio                                        | TIMESTAMP        | Data/hora do início                       | DEFAULT CURRENT\_TIMESTAMP      |
|                           | data\_fim                                           | TIMESTAMP        | Data/hora do término                      |                                 |
|                           | observacoes                                         | TEXT             | Observações do processo                   |                                 |
| **lead\_bruto**           | uc\_id                                              | TEXT             | Identificador da unidade consumidora      | PK                              |
|                           | import\_id                                          | TEXT             | Referência à importação                   | FK → import\_status(import\_id) |
|                           | cod\_id                                             | TEXT             | Código interno da UC (origem ANEEL/CCEE)  | NOT NULL                        |
|                           | distribuidora\_id                                   | INT              | Distribuidora responsável                 | FK → distribuidora(id)          |
|                           | origem                                              | origem\_enum     | Origem da UC (UCAT, UCMT, UCBT)           | NOT NULL                        |
|                           | ano                                                 | INT              | Ano de referência                         | NOT NULL                        |
|                           | status                                              | TEXT             | Status interno (`raw`, `processed`, etc.) | DEFAULT 'raw'                   |
|                           | data\_conexao                                       | DATE             | Data de conexão da UC                     |                                 |
|                           | cnae                                                | INT              | Código CNAE da atividade                  |                                 |
|                           | grupo\_tensao                                       | TEXT             | Grupo de tensão                           | FK → grupo\_tensao(id)          |
|                           | modalidade                                          | TEXT             | Modalidade tarifária                      | FK → modalidade\_tarifaria(id)  |
|                           | tipo\_sistema                                       | TEXT             | Tipo de sistema                           | FK → tipo\_sistema(id)          |
|                           | situacao                                            | TEXT             | Situação da UC                            | FK → situacao\_uc(id)           |
|                           | classe                                              | TEXT             | Classe de consumo                         | FK → classe\_consumo(id)        |
|                           | segmento                                            | TEXT             | Segmento de mercado                       | FK → segmento\_mercado(id)      |
|                           | subestacao                                          | TEXT             | Identificador da subestação               |                                 |
|                           | municipio\_id                                       | INT              | Código IBGE do município                  | FK → municipio(id)              |
|                           | bairro                                              | TEXT             | Bairro                                    |                                 |
|                           | cep                                                 | TEXT             | CEP da UC                                 |                                 |
|                           | pac                                                 | INT              | PAC (potência ativa contratada)           |                                 |
|                           | pn\_con                                             | TEXT             | Ponto notável de conexão                  |                                 |
|                           | descricao                                           | TEXT             | Observações gerais                        |                                 |
|                           | latitude                                            | DOUBLE PRECISION | Latitude geográfica                       |                                 |
|                           | longitude                                           | DOUBLE PRECISION | Longitude geográfica                      |                                 |
|                           | created\_at                                         | TIMESTAMP        | Timestamp de criação                      | DEFAULT CURRENT\_TIMESTAMP      |
|                           | updated\_at                                         | TIMESTAMP        | Timestamp de última atualização           | DEFAULT CURRENT\_TIMESTAMP      |
| **lead\_energia\_mensal** | uc\_id                                              | TEXT             | FK para `lead_bruto(uc_id)`               | PK, FK ON DELETE CASCADE        |
|                           | mes                                                 | INT              | Mês (1–12)                                | CHECK 1–12, PK                  |
|                           | energia\_ponta                                      | DOUBLE PRECISION | Energia no horário de ponta (MWh)         |                                 |
|                           | energia\_fora\_ponta                                | DOUBLE PRECISION | Energia fora de ponta (MWh)               |                                 |
|                           | energia\_total                                      | DOUBLE PRECISION | Energia total (MWh)                       |                                 |
|                           | origem                                              | origem\_enum     | Origem dos dados                          | NOT NULL                        |
| **lead\_demanda\_mensal** | ... e assim por diante para demanda e qualidade ... |                  |                                           |                                 |

> **Observação**: complete o dicionário para `lead_demanda_mensal`, `lead_qualidade_mensal`, `lead_enrichment_log` e `ponto_notavel` seguindo o mesmo padrão.

---

## 3. Diagrama ER

Utilize sua ferramenta favorita (pgModeler, DBeaver, Draw\.io) para gerar um diagrama ER com:

* Entidades e atributos principais.
* PKs sublinhadas.
* FKs indicadas como setas.
* Cardinalidades (1\:N) nos relacionamentos.

Você pode importar o SQL ou conectar diretamente ao Postgres e exportar o diagrama.

---

## 4. Exemplos de Queries Comuns

```sql
-- 1) Leads sem coordenadas definidas:
SELECT uc_id, cod_id
FROM lead_bruto
WHERE latitude IS NULL AND longitude IS NULL;

-- 2) Energia total por distribuidora/ano:
SELECT l.distribuidora_id, l.ano, SUM(e.energia_total) AS energia
FROM lead_bruto l
JOIN lead_energia_mensal e ON l.uc_id = e.uc_id
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

* Particione tabelas mensais (`lead_energia_mensal`, etc.) por coluna `ano` para agilizar consultas.
* Exemplo com declarative partitioning (Postgres 12+):

  ```sql
  CREATE TABLE lead_energia_mensal_2025 PARTITION OF lead_energia_mensal FOR VALUES IN (2025);
  ```
* Defina jobs para remover dados anteriores a N anos, se aplicável.

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

*Documentação gerada em: `$(date +'%Y-%m-%d')`*
