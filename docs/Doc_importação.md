# Documentação do Novo Pipeline de Importação

## Visão Geral

Este pipeline visa realizar a importação, normalização e inserção de dados oriundos dos arquivos GDB (Geodatabase) fornecidos pela ANEEL nas camadas `UCAT`, `UCMT`, `UCBT` e `PONNOT`. Cada camada é tratada por um script específico, mas todos compartilham uma base comum de funções no módulo `common_import_utils`.

---

## Estrutura do Pipeline

### 1. Orquestrador

**Arquivo**: `orquestrador.job.py`

* Itera sobre todos os `.gdb` em `data/downloads`.
* Determina distribuidora, ano e prefixo com base no nome do arquivo.
* Executa os importadores de forma sequencial com `subprocess.run()`.
* Evita reimportação se `import_status` estiver como "completed".

### 2. Scripts de Importação por Camada

* `importer_ucat_job.py`
* `importer_ucmt_job.py`
* `importer_ucbt_job.py`
* `importer_ponnot_job.py`

Cada um deles:

* Usa `argparse` para receber argumentos: `--gdb`, `--ano`, `--distribuidora`, `--prefixo`, `--modo_debug`
* Detecta a camada correta com `detectar_layer()`
* Lê o `gdf` com geopandas
* Remove colunas sujas e padroniza valores nulos
* Extrai `dist_id` e gera `import_id`
* Chama `normalizar_dataframe_para_tabelas()` para gerar os dataframes normalizados (exceto `PONNOT`)
* Realiza `copy_to_table` para cada tabela: `lead_bruto`, `lead_energia_mensal`, `lead_qualidade_mensal`, `lead_demanda_mensal`
* Registra status em `import_status`

### 3. Funções Utilitárias

**Módulo**: `common_import_utils.py`

* `detectar_layer(gdb_path, prefixo)`: encontra a camada correta dentro do .gdb
* `gerar_uc_id(cod_id, ano, camada, distribuidora_id)`: gera um hash determinístico com SHA256 para identificar a UC
* `copy_to_table(conn, df, table)`: realiza COPY otimizado via `StringIO`
* `normalizar_dataframe_para_tabelas(...)`: transforma o gdf em 4 dataframes normalizados:

  * `lead_bruto`
  * `lead_energia_mensal`
  * `lead_qualidade_mensal`
  * `lead_demanda_mensal`

### 4. Campos Padronizados por Camada

#### UCAT

* Energia: `ENE_P_MM`, `ENE_F_MM`
* Demanda: `DEM_P_MM`, `DEM_F_MM`, `DEM_CONT`
* Qualidade: `DIC_MM`, `FIC_MM`, `SEMRED`

#### UCMT

* Energia: `ENE_MM`
* Demanda: `DEM_MM`, `DEM_CONT`
* Qualidade: `DIC_MM`, `FIC_MM`, `SEMRED`

#### UCBT

* Energia: `ENE_MM`
* Demanda: `DEM_MM` (aparece repetido nas 3 colunas)
* Qualidade: `DIC_MM`, `FIC_MM`

#### PONNOT

* Apenas extração de geometria (latitude/longitude) e inserção na tabela `ponto_notavel`

---

## Tabelas de Destino

* `lead_bruto`
* `lead_energia_mensal`
* `lead_demanda_mensal`
* `lead_qualidade_mensal`
* `ponto_notavel`
* `import_status`

---

## O que deve ir para `common_import_utils`

**Manter**:

* `detectar_layer`
* `gerar_uc_id`
* `copy_to_table`
* `normalizar_dataframe_para_tabelas`
* `validar_df_bruto`

**Possível mover**:

* Mapeamentos dos campos por camada (UCAT, UCMT, UCBT)

  * Criar uma pasta `config/` com `campos_ucat.py`, `campos_ucmt.py`, `campos_ucbt.py` com listas pré-definidas para os campos esperados

---

## Vantagens do Novo Pipeline

* Modularidade total: cada camada possui seu script independente e limpo
* Reuso de lógica comum via `common_import_utils`
* Controle de estado com `import_status`
* Integração com SWR e frontend reativo
* Logs robustos com `tqdm.write`
* Facilidade para debugger com `--modo_debug`

---

Pronto para documentar agora os fluxos de inserção, enriquecimento e versão futura se quiser!
