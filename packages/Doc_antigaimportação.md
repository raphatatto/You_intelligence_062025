# 📃 Documentação Técnica: Pipeline Antigo de Importação GDB (pré-refatoração)

## Objetivo

Registrar o funcionamento do pipeline de ingestão de dados das camadas UCAT, UCMT e UCBT antes da refatoração para arquitetura modularizada com `common_import_utils.py`.

---

## ✅ Estrutura Geral

Cada script (UCAT, UCMT, UCBT) era independente e continha:

* Leitura da camada com `gpd.read_file`
* Limpeza de colunas (colunas "sujas" removidas com regex)
* Construção de `df_bruto`, `df_energia`, `df_demanda`, `df_qualidade` diretamente
* COPY para banco direto via `get_db_cursor()`
* Registro de status via SQL direto

---

## ☑️ UCAT

### 1. Leitura

```python
gdf = gpd.read_file(gdb_path, layer="UCAT_tab")
```

### 2. DataFrame lead\_bruto

Campos:

* `id`, `id_interno`, `cnae`, `grupo_tensao`, `modalidade`, `tipo_sistema`, `situacao`, `distribuidora`, `origem`, `status`, `data_conexao`, `classe`, `segmento`, `subestacao`, `municipio_ibge`, `bairro`, `cep`, `pac`, `pn_con`, `descricao`

### 3. DataFrames normalizados

* `df_demanda`: DEM\_P\_*, DEM\_F\_* → arrays via `_to_pg_array`
* `df_energia`: ENE\_P\_\* + ENE\_F\_\*, DEM\_CONT → energia, potencia
* `df_qualidade`: DIC\_*, FIC\_* → arrays

### 4. COPY explícito

```python
cur.copy_expert("COPY lead_bruto (...) FROM STDIN", buf)
```

### 5. Registro de status

Direto via SQL INSERT/UPDATE na tabela `import_status`

---

## ☑️ UCMT / UCBT

### Diferenças em relação ao UCAT:

* `segmento` estava presente, mas `subestacao` nem sempre.
* `UCBT` usava `CAR_INST` como campo de `potencia`, ao invés de `DEM_CONT`
* `df_energia`, `df_qualidade` e `df_demanda` seguiam lógica similar

### Remoção de duplicados:

Com checagem SQL:

```python
cur.execute("SELECT id FROM lead_bruto WHERE id = ANY(%s)", (list(df_bruto["id"]),))
```

### Limpeza de colunas sujas

Detectada via:

```python
df.astype(str).apply(lambda col: col.str.contains("106022|YEL", na=False))
```

### COPY final

Feito para:

* `lead_bruto`
* `lead_demanda`
* `lead_energia`
* `lead_qualidade`

---

## 🔗 Conclusão

O modelo antigo era funcional, mas:

* Continha **muita repetição de código**
* Não havia controle por `import_id`
* `uc_id` não era hash: usava `COD_ID` diretamente como chave
* Lógica de limpeza, parsing e COPY estava embutida em cada script

Essa documentação serve de base para compararmos com a nova estrutura modularizada e tomarmos decisões técnicas sobre o que deve permanecer centralizado no `common` e o que é específico de cada script.
