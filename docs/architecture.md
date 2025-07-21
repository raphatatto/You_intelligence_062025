You.On Intelligence – Plataforma de Inteligência de Mercado em Energia
Visão Geral do Projeto
O You.On Intelligence é um projeto que transforma dados brutos do setor elétrico – provenientes da ANEEL e outras fontes públicas – em informações estratégicas para a empresa You.On
GitHub
. Em outras palavras, a plataforma consolida milhões de registros para produzir leads qualificados (potenciais clientes) para ofertas comerciais (como Arbitragem, Backup, GTD), gerar insights geoespaciais sobre consumo e demanda, indicadores de qualidade de energia (DIC/FIC) e oferecer dashboards administrativos além de uma API de consulta dos dados
GitHub
. Problema: Historicamente, a análise de mercado de energia dependia da base regulatória BDGD (Base de Dados Geográfica da Distribuidora), que apresentava limitações importantes: atualizações infrequentes, acesso descentralizado (cada concessionária publica separadamente) e dificuldade de integrar com outras fontes. Isso significava trabalhar com dados estáticos e esforço manual de consolidação, sem garantia de atualização consistente. Solução e Objetivo: O You.On Intelligence surgiu para superar esses gargalos, substituindo a dependência direta da BDGD por uma abordagem de dados abertos automatizada. Os dados de unidades consumidoras passaram a ser obtidos de fontes públicas centralizadas (por exemplo, o portal ArcGIS Hub da ANEEL via API), com maior frequência de atualização e pipeline automatizado de ETL. Além disso, a plataforma cruza os dados elétricos com outras bases (mercado livre via CCEE, dados cadastrais via Receita Federal, dados socioeconômicos do IBGE, etc.), criando uma base de inteligência geográfica ampla e sempre atualizada. Impacto Esperado: Com essa solução, a You.On pode visualizar a malha elétrica e a distribuição de consumo no território, identificar clusters de alta demanda ou de geração distribuída, acompanhar a qualidade do serviço por região e localizar clientes potenciais para migração ao mercado livre ou ofertas de backup. Em suma, o sistema permite extrair valor dos dados – transformando-os em inteligência acionável para tomada de decisão estratégica e novas oportunidades de negócio.
Arquitetura e Componentes
A arquitetura do You.On Intelligence é composta de vários componentes integrados, garantindo desde a ingestão de dados crus até a entrega de insights em interfaces amigáveis. A seguir, destacamos os principais elementos:
Camadas de dados ANEEL (UCAT, UCMT, UCBT): A base de dados primária vem dos arquivos geográficos padronizados pela ANEEL (BDGD/SIG-R). Esses arquivos estão organizados em camadas referentes ao tipo de unidade consumidora por tensão: UCAT (Unidades Consumidoras de Alta Tensão), UCMT (Média Tensão) e UCBT (Baixa Tensão). Juntas, essas fontes cobrem praticamente todas as unidades consumidoras do país (dezenas de milhões de pontos). Cada camada traz atributos técnicos (como cargas, demandas, qualidade) georreferenciados por coordenadas ou por referência de rede elétrica. Há também a camada PONNOT (Pontos Notáveis) que representa pontos de conexão notáveis da rede elétrica – por exemplo, coordenadas de transformadores ou chaves – utilizada como referência de localização adicional
GitHub
GitHub
.
Pipeline de Ingestão de Dados: Arquivos abertos da ANEEL (como geodatabases .gdb anuais de cada distribuidora) são importados automaticamente em lote. Jobs ETL em Python leem as camadas (UCAT, UCMT, UCBT, etc.) e realizam a transformação e normalização dos dados para o formato relacional interno
GitHub
. Esse processo inclui limpeza de inconsistências, geração de chaves únicas (hashes de IDs das UCs + ano + camada) e separação de dados em tabelas normalizadas (metadados de unidades, séries mensais, etc). A orquestração dessas tarefas fica a cargo do Apache Airflow, que programaticamente coordena as importações e garante reprocessamento periódico quando novos dados são disponibilizados
GitHub
.
Enriquecimento de Dados Externos: Após a ingestão bruta, o sistema executa etapas de enriquecimento, adicionando informações que não constam nos arquivos originais. Exemplos: consulta a APIs externas para obter dados cadastrais de CNPJ/CNAE (classificação da empresa por atividade econômica), coordenadas geográficas adicionais (via serviços GIS quando a coordenada exata não é fornecida) e até integração de dados climáticos ou populacionais para contextualizar análises
GitHub
GitHub
. Um caso prático é a utilização do campo de ponto notável (PN_CON) da UC para recuperar coordenadas de referência: se uma unidade não possui latitude/longitude individual, o sistema associa o código de ponto de conexão (PN_CON) à tabela de pontos notáveis e recupera a coordenada daquele transformador ou estrutura, garantindo localização para 100% das unidades
GitHub
GitHub
. Além disso, o CNAE de unidades empresariais é cruzado com um dicionário interno para atribuir um segmento de mercado estimado a cada lead (industrial, comercial, residencial, etc.)
GitHub
.
Banco de Dados Relacional (intel_lead): Todos os dados processados residem em um banco PostgreSQL (com extensões GIS para manipulação geográfica). O schema principal, chamado intel_lead, foi desenhado para armazenar de forma eficiente e segmentada os dados das unidades consumidoras. Há tabelas principais de leads (dados técnicos estáticos da unidade), tabelas de séries temporais mensais (energia, demanda e qualidade mês a mês por UC) e diversas tabelas de domínio (cadastros normalizados como tabelas de municípios, classes de consumo, grupos de tensão, etc.) – todos interligados por chaves estrangeiras
GitHub
. Esse design relacional evita redundância e facilita consultas analíticas complexas. O banco conta também com índices nas colunas mais usadas (por exemplo, índice por UC, por distribuidora, por ano) para garantir desempenho nas consultas mesmo com volume grande de dados
GitHub
. Vale mencionar que o banco recebe inserts em massa via COPY (otimizando a carga de milhões de registros por vez) e suporta operações de geolocalização via tipos PostGIS (ex.: cálculos de distância, pontos em polígonos, etc).
Camada Analítica – Views e Materialized Views: Sobre o schema bruto foram construídas diversas views SQL que facilitam o consumo dos dados pela API e por analistas, sem expor diretamente as tabelas normalizadas. Por exemplo, a view **lead_com_coordenadas** já une a tabela de leads com a tabela de ponto notável, adicionando a coordenada final de cada unidade (priorizando a própria coordenada da UC se disponível, ou a do ponto notável como fallback)
GitHub
. Outras views enriquecidas combinam dados técnicos com descrições (ex.: vw_lead_com_cnae_desc junta o código CNAE da unidade com a descrição textual da atividade econômica correspondente)
GitHub
. Também foram criadas views materializadas para agregações frequentes, melhorando a performance de consulta no painel/admin: por exemplo **resumo_energia_por_municipio** sumariza a energia total consumida e quantidade de leads por município
GitHub
. Essas views materializadas podem ser atualizadas sob demanda conforme novos dados são importados (via comando REFRESH MATERIALIZED VIEW)
GitHub
. Em resumo, a camada de views oferece diferentes visões derivadas – desde visão completa por lead (vw_lead_completo_detalhado) até resumos por distribuidora ou ano – prontas para uso nas interfaces e análises
GitHub
GitHub
.
API REST e Painel Administrativo: Para expor as informações de maneira acessível, o projeto inclui um backend em Python (FastAPI) que provê uma API RESTful com endpoints seguros para consultar os dados de inteligência. Essa API aproveita as views mencionadas, fornecendo respostas já agregadas ou enriquecidas conforme a necessidade (por exemplo, endpoint para obter todos os detalhes de um lead específico ou listar resumo de consumo por município). Em paralelo, um painel web administrativo foi desenvolvido em Next.js/React (frontend) integrado à API, oferecendo à equipe da You.On uma interface gráfica para explorar os leads, visualizar mapas e gráficos e acompanhar o status das importações
GitHub
. O painel permite, por exemplo, filtrar unidades por região ou perfil, visualizar no mapa as unidades com maiores demandas, e verificar logs de enriquecimento ou alertas. A arquitetura web segue boas práticas de segurança e usabilidade, incluindo autenticação JWT para acesso aos dados sensíveis e restrição de acesso administrativo por VPN/IP
GitHub
. Com essa combinação de API + Frontend, tanto stakeholders técnicos (via API e SQL) quanto usuários de negócio (via dashboard intuitivo) conseguem interagir com a plataforma de inteligência de forma adequada às suas necessidades.
(Diagrama de diretórios e stack tecnológica: ver README do repositório para detalhes sobre a organização em módulos de apps (API, frontend), packages (jobs ETL, AI, database), infraestrutura (Docker, Terraform) etc
GitHub
.)
Banco de Dados e Regras de Modelagem
O schema intel_lead no PostgreSQL concentra a modelagem dos dados de inteligência, projetada para manter a integridade referencial, facilitar atualizações e espelhar os conceitos do setor elétrico conforme o padrão regulatório. Abaixo detalhamos os principais elementos dessa modelagem: tabelas, domínios, enums (enumeradores), além de regras e exemplos de uso SQL.
Tabelas Principais (Fato das UCs)
lead_bruto – Armazena os dados básicos de cada Unidade Consumidora (UC) importada. Cada registro representa uma UC em um determinado ano e camada (AT, MT ou BT). Campos principais incluem: identificadores (chave primária uc_id gerada via hash do código + ano + camada
GitHub
), código original da UC na distribuidora (cod_id), distribuidora (chave estrangeira para tabela de distribuidoras), ano de referência, camada de origem (UCAT/UCMT/UCBT)
GitHub
, status de processamento (ex.: 'raw' inicialmente), e diversos atributos técnicos como data de conexão (data_conexao), código CNAE, grupo de tensão, modalidade tarifária, tipo de sistema (mono/trifásico, etc), situação da UC (ativa/inativa), classe de consumo (residencial, industrial, etc), segmento de mercado (inferido via CNAE), localização (códigos de município, bairro, CEP) e indicadores elétricos estáticos (ex.: PAC – Potência Ativa Contratada, em kW)
GitHub
GitHub
. O campo pn_con guarda o código do ponto de conexão associado (se fornecido), possibilitando relacionar com coordenadas de um ponto notável. Por fim, campos de auditoria created_at e updated_at registram timestamps de criação/atualização. A lead_bruto é a tabela central – cada UC aparece uma vez por ano por origem – sobre a qual as demais tabelas se relacionam. Índices existem nas colunas mais consultadas, como (distribuidora_id, ano) e pn_con para agilizar buscas por área ou conexão
GitHub
.
Tabelas de Séries Temporais: Para armazenar os dados mensais de cada UC, existem três tabelas relacionais, todas ligadas à lead_bruto via chave estrangeira uc_id:
lead_energia_mensal – Armazena a energia consumida por mês, separada por ponta e fora-ponta quando aplicável. Cada registro tem uc_id, mes (1 a 12) e valores de energia (kWh) consumida em horário de ponta e fora de ponta, além do total
GitHub
. Em unidades de média tensão (MT), por exemplo, geralmente só há medição total, então o valor aparece em energia_total e energia_ponta enquanto energia_fora_ponta pode ficar nulo
GitHub
. A chave primária composta (uc_id, mes) garante unicidade do mês por unidade e facilita operações de pivot.
lead_demanda_mensal – Armazena a demanda elétrica (kW) por mês. Inclui campos para demanda na ponta, fora-ponta, total e demanda contratada da UC naquele mês
GitHub
GitHub
. Como na energia, para certos perfis de tensão pode haver apenas demanda total; os campos não usados ficam nulos. Também possui PK composta (uc_id, mes).
lead_qualidade_mensal – Armazena indicadores de qualidade por mês, em especial DIC (Duração de Interrupção por UC, em horas) e FIC (Frequência de Interrupção por UC) acumulados no mês, além de horas sem fornecimento (semrede)
GitHub
. Esses indicadores vêm dos relatórios de continuidade da distribuidora. PK composta (uc_id, mes).
Todas as tabelas mensais usam chave estrangeira para lead_bruto(uc_id) com ação ON DELETE CASCADE, ou seja, se um lead for removido (por exemplo, para corrigir duplicidade), seus registros mensais associados são excluídos automaticamente, mantendo consistência referencial
GitHub
GitHub
. Da mesma forma, ao inserir dados, o banco assegura que não existam séries mensais sem o respectivo lead cadastrado.
Tabelas de Controle e Log:
import_status – Controla o status das importações de cada conjunto de arquivos. Cada linha representa uma execução de importação (identificada por um import_id único) contendo informações como: distribuidora alvo, ano, camada importada (UCAT, UCMT, UCBT ou PONNOT), status do processo (pending, running, completed, failed)
GitHub
, quantidade de linhas processadas e timestamps de início/fim
GitHub
. Essa tabela permite rastrear o progresso das cargas e registrar eventuais erros ou observações. Por exemplo, ao iniciar a importação dos dados UCMT 2024 de uma concessionária, cria-se um registro com status "running", e ao finalizar atualiza-se para "completed" com total de linhas inseridas.
lead_enrichment_log – Registra logs das etapas de enriquecimento realizadas em cada lead. Cada entrada possui um ID, referência à UC (uc_id), descrição da etapa (por exemplo "geocoding", "CNPJ lookup"), resultado (success, partial ou failed) e detalhes adicionais ou mensagens de erro
GitHub
. Assim, é possível auditar o que foi acrescentado a cada lead e diagnosticar falhas no pipeline (ex: um log indicativo de falha ao buscar coordenadas via API externa para determinada UC).
Tabelas de Domínio e Enumeradores
Para evitar redundância e aderir a valores padronizados, o schema define várias tabelas de domínio que servem como referência para atributos categóricos das UCs. Essas tabelas tipicamente possuem um campo id (código ou sigla) e uma descricao. As principais são:
distribuidora – Lista todas as concessionárias de energia consideradas, com um código numérico (id) e nome (ex: id 383 = "Enel RJ")
GitHub
.
municipio – Tabela de municípios brasileiros, relacionando código IBGE (id), nome e UF (estado)
GitHub
. Usada para referenciar o município de cada UC (municipio_id em lead_bruto).
grupo_tensao – Domínio dos grupos de tensão de atendimento, por exemplo AT (Alta Tensão), MT (Média), BT (Baixa), cada um com um código e descrição
GitHub
.
modalidade_tarifaria – Tipos de modalidade tarifária (convencional, branca, azul, verde, etc.) identificados por código
GitHub
.
tipo_sistema – Tipo de sistema de conexão da UC, por exemplo, monofásico, trifásico, ou outras categorias definidas pela ANEEL
GitHub
.
classe_consumo – Classes de consumo da UC (residencial, industrial, comercial, rural, etc.), cada qual indicando se o cliente é pessoa física (PF) ou jurídica (PJ). A tabela contém um campo tipo_cliente que aceita apenas 'PF' ou 'PJ', restrito via CHECK constraint no banco
GitHub
.
situacao_uc – Situação da unidade consumidora, por exemplo ativa, cortada, suprimida, etc., conforme as definições da distribuidora/ANEEL
GitHub
.
segmento_mercado – Segmento de mercado inferido a partir do CNAE: por exemplo, comércio, serviços, manufatura, poder público, etc. Este campo é preenchido durante o enriquecimento cruzando o CNAE principal do cliente PJ com uma classificação setorial definida (por enquanto de forma estática ou manual)
GitHub
.
cnae – Tabela de referência de Códigos CNAE (Classificação Nacional de Atividades Econômicas) para descrição de atividade. Permite, dado um código CNAE, obter o texto do ramo de atividade da empresa. Essa tabela auxilia a preencher o segmento_mercado e também pode ser usada para filtragens (ex: listar todos leads do setor "Indústria de Alimentos").
ponto_notavel – Armazena coordenadas geográficas de pontos notáveis da rede elétrica, usados como referência de localização. Cada ponto tem um identificador único pn_id (gerado via hash combinando nome, coordenadas, ano e distribuidora
GitHub
), a latitude/longitude e possivelmente um nome/descritivo e CEP relacionado
GitHub
. Quando uma UC possui em seu dado de origem um código de ponto de conexão (PN_CON), podemos buscar neste cadastro a localização exata desse ponto caso a UC não venha com coordenadas próprias. Em termos de base ANEEL, essa tabela representa a camada PONNOT importada dos geodatabases das distribuidoras.
Todas essas tabelas de domínio são ligadas via foreign keys às colunas correspondentes em lead_bruto (ou em outras tabelas). Assim, o banco garante que, por exemplo, o código de modalidade tarifária em um lead exista na tabela modalidade_tarifaria, ou que o município referenciado exista na tabela municipio. Isso normaliza a base e facilita atualizações de nomenclatura (basta alterar na tabela de domínio para refletir em todos leads relacionados). Além das tabelas, o schema define tipos enumerados (ENUM) para certos campos padronizados:
camada_enum – Representa a camada de origem do dado importado: valores possíveis UCAT, UCMT, UCBT ou PONNOT
GitHub
.
origem_enum – Similar à camada, indica a origem dos dados de um registro, mas focado apenas nas UCs (UCAT, UCMT, UCBT)
GitHub
. Por exemplo, as tabelas de energia/demanda/qualidade mensais usam este campo para marcar se aquele dado veio do conjunto de alta, média ou baixa tensão.
status_enum – Usado em import_status para indicar o estado de uma importação: pending (pendente/não iniciada), running (em execução), completed (concluída) ou failed (falhou)
GitHub
.
resultado_enum – Usado em lead_enrichment_log para resultado de cada etapa de enriquecimento: success (sucesso completo), partial (parcial, ex: alguns dados enriquecidos, outros não) ou failed (falha na etapa)
GitHub
.
Os enumeradores garantem consistência semântica – por exemplo, uma importação não terá status fora dos quatro previstos, evitando valores livres inconsistentes.
Regras de Integridade e Qualidade dos Dados
A modelagem do intel_lead incorpora diversas regras de integridade para assegurar a qualidade e coerência dos dados:
Chaves Estrangeiras e Cascade: Conforme mencionado, todas as relações mestre-detalhe usam foreign keys com integridade referencial. Isso impede, por exemplo, inserir um lead_energia_mensal com um uc_id inexistente em lead_bruto, ou excluir uma distribuidora que ainda tenha leads associados. Quando exclusões precisam ocorrer (como remoção de um lead duplicado), o ON DELETE CASCADE nas FKs de séries mensais garante limpeza completa dos dados relacionados
GitHub
, evitando lixo residual no banco.
Constraints e Checks: Alguns campos críticos possuem restrições de domínio. Por exemplo, o campo tipo_cliente em classe_consumo só aceita 'PF' ou 'PJ'
GitHub
, evitando erro de digitação. Da mesma forma, campos numéricos de mês têm CHECK (mes BETWEEN 1 AND 12) aplicado, etc. Esses checks básicos contribuem para capturar anomalias logo na carga.
Triggers de Proteção: Para evitar alterações manuais indevidas em tabelas de referência, foram implementados gatilhos (triggers) que bloqueiam operações não autorizadas. Tabelas como cnae, municipio, grupo_tensao e outras de domínio são essencialmente estáticas – modificá-las acidentalmente poderia corromper a consistência dos leads. Assim, essas tabelas estão protegidas por triggers que, por padrão, impedem updates/deletes diretos (somente permitindo alteração mediante desabilitação explícita do trigger, o que previne alterações acidentais)
GitHub
. Essa política confere uma camada extra de segurança aos dados de referência. Por exemplo, se alguém tentar deletar todos municípios, o trigger abortará a transação a menos que seja intencionalmente desligado o mecanismo de proteção.
Auditoria e Monitoramento: A existência das tabelas import_status e lead_enrichment_log citadas anteriormente também é parte da integridade lógica do sistema. Elas funcionam como trilhas de auditoria, permitindo identificar quando e como cada registro entrou no banco e se passou por todas etapas de enriquecimento com sucesso. Isso ajuda a detectar possíveis problemas (e.x., uma importação marcada como failed sinaliza que aquele lote de dados não foi completamente carregado e precisa de atenção).
Exemplos de Consultas Reais
A seguir, apresentamos algumas queries SQL de exemplo já utilizadas para extrair inteligência da base – ilustrando como os dados podem ser combinados:
Leads com enriquecimento completo e PAC elevado: Identifica unidades consumidoras que já foram totalmente enriquecidas (status de enriquecimento 'success') e que possuem potência contratada muito alta (acima de 15.000 kW, indicando clientes de grande porte). Essas UCs são potenciais alvos para ofertas comerciais específicas, dada sua relevância em consumo:
sql
Copiar
Editar
SELECT * 
FROM vw_lead_completo_detalhado
WHERE enriquecimento_status = 'success'
  AND pac > 15000;
Explicação: usa a view consolidada vw_lead_completo_detalhado (que já junta dados brutos, enriquecidos e agregados) filtrando apenas leads com status de enriquecimento de sucesso e PAC acima do limite estabelecido. A consulta retorna todas as colunas do lead, permitindo análise detalhada de cada caso
GitHub
.
Leads com DIC/FIC acima da média: Lista unidades com indicadores de qualidade muito piores que o normal – por exemplo DIC (duração de interrupções) maior que 10 horas ou FIC (frequência de interrupções) maior que 15 no período considerado:
sql
Copiar
Editar
SELECT * 
FROM vw_lead_completo_detalhado
WHERE media_dic > 10
   OR media_fic > 15;
Explicação: esta query aproveita colunas calculadas na view completa que trazem a média de DIC e média de FIC daquela UC (provinda dos dados de qualidade mensais). Filtramos por critérios definidos de exceção. O resultado permite identificar clientes/localidades com qualidade de fornecimento insatisfatória – insight útil para direcionar ações de melhoria ou comunicação proativa com esses consumidores
GitHub
.
(Observação: As views como vw_lead_completo_detalhado agregam os valores mensais calculando médias e somas – por exemplo, media_dic e media_fic são derivadas dos 12 valores mensais de cada UC – facilitando esse tipo de filtro global.)
Relação com o Modelo da ANEEL (BDGD/SIG-R)
Toda a estrutura do intel_lead foi concebida alinhada ao modelo regulatório da ANEEL, espelhando nomenclaturas e chaves presentes na BDGD e no sistema SIG-R. Isso traz diversos benefícios: facilidade de atualização com novos dados regulatórios, capacidade de join direto com outras tabelas da ANEEL e entendimento padronizado dos campos por parte de usuários do setor elétrico. Em termos práticos, os arquivos abertos da ANEEL já seguem um dicionário de dados unificado (Dicionário de Dados ANEEL - DDA do SIG-R). Por exemplo, campos como COD_ID (código da UC), MUN (código do município), GRU_TEN (grupo de tensão), CLAS_SUB (classe de consumo) vêm documentados no manual da BDGD e foram importados sem alteração de significado, apenas traduzidos para nomes mais intuitivos no banco (quando necessário) e normalizados em tabelas de domínio. Os valores categóricos atendem aos padrões do módulo 10 dos Procedimentos de Distribuição (PRODIST) da ANEEL, garantindo que todas as distribuidoras compartilhem o mesmo esquema de entidades e atributos. Em suma, o nosso schema interno é praticamente um reflexo da BDGD: as entidades da ANEEL (UCs AT/MT/BT, pontos notáveis, etc.) correspondem diretamente às nossas tabelas, e os atributos (colunas) correspondem aos campos do SIG-R – apenas reorganizados de forma relacional. Essa aderência ao modelo ANEEL traz compatibilidade e confiabilidade. Podemos cruzar facilmente nossos dados com outros conjuntos abertos do setor elétrico (tarifas, indicadores por município, etc.), pois usamos as mesmas chaves (códigos de concessionária, códigos IBGE de municípios, códigos CNAE, etc). Além disso, ao chegar novas versões da BDGD (que ocorrem anualmente), o processo de ingestão consegue mapear os campos automaticamente, já que seguimos a mesma definição de dicionário de dados. Em resumo, aproveitamos o melhor dos dados abertos regulatórios padronizados e os incorporamos à inteligência da You.On, evitando reinvenções e garantindo que os insights produzidos sejam calcados em informações oficiais e comparáveis setorialmente.
Linha do Tempo do Projeto
O desenvolvimento do You.On Intelligence foi estruturado em fases, cada uma focada em entregar componentes-chave da solução e expandir suas capacidades. A seguir, apresentamos uma breve linha do tempo, destacando marcos já concluídos, o estágio atual e próximos passos planejados:
Fase 1 – Fundamentos (Ideação até Q1 2024): Concepção do projeto e setup da infraestrutura básica. Nesta etapa inicial, focou-se em criar o pipeline ETL capaz de ingerir a enorme base BDGD da ANEEL. Foram desenvolvidos os scripts de importação para UCAT, UCMT e UCBT, testados inicialmente com dados de uma distribuidora piloto. Em paralelo, definiu-se o modelo relacional intel_lead e carregou-se um primeiro lote de dados históricos (ano base 2022/2023) para validação. O sucesso dessa fase foi comprovar que a plataforma conseguia manejar milhões de registros de forma consistente e performática em um ambiente de teste.
Fase 2 – Enriquecimento e Expansão de Dados (Q2–Q3 2024): Com a base técnica pronta, a próxima fase integrou novas fontes de dados externas para enriquecer os leads. Foi implementada a importação da camada PONNOT (pontos notáveis), adicionando coordenadas geográficas detalhadas aos pontos de conexão
GitHub
. Também começou a integração de dados de CNAE/CNPJ: foi carregada uma tabela de CNAEs e desenvolvida rotina para associar cada UC de pessoa jurídica a um código CNAE válido (usando o CNPJ do cliente quando disponível) – permitindo assim inferir o segmento de mercado do lead
GitHub
. Adicionalmente, incluiu-se uma base de municípios IBGE e códigos de distribuidoras para unificar chaves e possibilitar cruzamentos com fontes governamentais. Ao final desta fase, o sistema já contava com um dataset unificado combinando dados técnicos da ANEEL com informações geográficas e de mercado, pronto para análises mais profundas. Também foi aqui que se implementou o Airflow para orquestração, agendando as importações de forma automatizada (por exemplo, verificar e baixar novas atualizações anuais da BDGD assim que disponibilizadas pela ANEEL).
Fase 3 – Aplicações e Interface (Q4 2024 – Q1 2025): Nesta etapa, o foco foi expor a inteligência gerada de forma acessível aos usuários finais. Desenvolveu-se a API REST usando FastAPI, com endpoints para consultar leads, filtros (por distribuidora, região, segmento, etc) e obtenção de agregados. Em paralelo, foi criado o painel administrativo web (frontend Next.js) para uso interno, incluindo visualizações geográficas interativas (mapas mostrando densidade de consumo, por exemplo) e gráficos temporais de demanda e qualidade. Essa interface passou por refinamentos com feedback das equipes técnicas e de negócios, garantindo que mesmo usuários não técnicos pudessem navegar pelos insights. Nesta fase também foram implementadas views materializadas e otimizações no banco para suportar consultas complexas do painel em tempo real (por exemplo, um resumo por município carregando instantaneamente após atualização via REFRESH). Até o início de 2025, a plataforma encontrava-se em piloto interno, com dados de várias concessionárias já carregados e atualizados até 2023. As áreas de inteligência de mercado passaram a usar o sistema para identificar novos leads potenciais e avaliar indicadores de qualidade de energia em reuniões estratégicas.
Estágio Atual – Consolidação (Meados de 2025): No momento, o You.On Intelligence está em processo de consolidação e hardening. Isso envolve aprimorar a qualidade dos dados (por exemplo, checagens de consistência entre consumo e demanda, tratamento de outliers nos indicadores de qualidade) e reforçar a infraestrutura para ambiente de produção (como implementar redundâncias, backups e monitoramento de desempenho). A plataforma já integra diversas fontes externas além da ANEEL – incluindo dados da CCEE (sobre mercado livre e consumo por segmento) e indicadores socioeconômicos do IBGE –, enriquecendo ainda mais as análises disponíveis
GitHub
. A ênfase agora é garantir que as atualizações anuais da BDGD ocorram de forma pontual e transparente (idealmente com mínima intervenção manual, via automação completa do Airflow), e preparar o caminho para as funcionalidades avançadas planejadas.
Próximos Marcos – Inteligência Avançada (final de 2025 em diante): Com a base de dados madura, os próximos passos focam em extrair insights ainda mais inteligentes dos dados. Há um roadmap para implementar funcionalidades de analytics e machine learning de alto impacto – conforme descritas na seção a seguir de Visão Futura. Entre os marcos previstos, destacam-se: ferramentas de clusterização geográfica para segmentar automaticamente a base de UCs por perfil de consumo/localização
GitHub
, cálculo de score de leads combinando múltiplos critérios (demanda, custo, inadimplência média da região, etc) para priorização comercial, e modelos preditivos capazes de estimar o crescimento de consumo ou detectar anomalias de perdas técnicas. A integração com sistemas legados também está no horizonte, como expor uma API pública (ou portal) para que parceiros e outras áreas consumam os dados, além de conectar com o CRM da empresa para alimentação automática de informações dos leads gerados. Esses desenvolvimentos buscarão posicionar o You.On Intelligence não apenas como um repositório de dados, mas como uma ferramenta proativa, gerando recomendações e alertas que apoiem decisões em tempo real. (Ver próximos tópicos para mais detalhes sobre essa visão futura.)
Visão Futura (O Sonho)
O horizonte de evolução do You.On Intelligence contempla diversas funcionalidades de alto impacto que transformarão a plataforma em um hub de inteligência energética completa. Abaixo listamos algumas das principais ideias e recursos sonhados, orientados tanto pela dor dos usuários quanto pelas tendências tecnológicas no setor elétrico:
Visualização Geográfica Interativa: Implementar mapas interativos avançados no painel, permitindo navegar pelos dados spatialmente. Por exemplo, heatmaps de consumo elétrico por bairro, sobreposição de camadas (rede elétrica, densidade populacional) e ferramentas de seleção geográfica (desenhar polígonos no mapa para filtrar UCs dentro de uma área). Essa funcionalidade tornará a análise visual e intuitiva, auxiliando stakeholders a identificarem regiões críticas ou oportunidades de mercado de forma imediata.
Prospecção Inteligente (Lead Scoring Automatizado): Desenvolver um sistema de pontuação de leads baseado em critérios múltiplos, para priorizar quais unidades consumidoras têm maior potencial para determinadas ofertas. Por exemplo, um score que combine consumo elevado, baixo índice de qualidade (indicando insatisfação), segmento industrial e localização em área estratégica poderia indicar um ótimo candidato para oferta de solução de backup ou migração ao mercado livre. Esse recurso usaria algoritmos de aprendizado (p.ex. regressão ou árvore de decisão treinada com histórico de conversão de clientes) para recomendar ao time comercial quais leads abordar primeiro – em essência, um sistema de recomendação de prospects energéticos
GitHub
.
Previsão de Consumo e Detecção de Perdas com ML: Alavancar técnicas de machine learning para analisar as séries temporais de consumo/demanda e prever tendências futuras. Modelos de previsão (como ARIMA, LSTM, Prophet) poderiam estimar o consumo de energia de uma UC nos próximos meses, ou identificar padrões anômalos que sugiram perdas técnicas ou comerciais. Por exemplo, detectar queda abrupta de consumo em uma área que possa indicar migração de clientes para concorrentes, ou consumo não técnico (desvios) em determinada região. Esses insights preditivos ajudariam tanto na planejamento de oferta (dimensionar contratos futuros) quanto na melhoria operacional (foco em inspeções onde há suspeita de perda).
API Pública e Integração com CRM: Evoluir a arquitetura de forma a disponibilizar uma API externa (ou via módulo de integração) para que sistemas parceiros ou clientes autorizados possam consultar alguns dados de forma segura. Isso habilitaria, por exemplo, a criação de aplicativos externos ou relatórios customizados sob demanda. Em paralelo, a integração direta com o CRM da You.On permitiria que todo lead identificado como qualificado na plataforma fosse automaticamente enviado para o funil de vendas, mantendo os times de venda sempre abastecidos com as informações mais recentes (eliminação de processos manuais de export/import). A API pública também reforça a imagem da You.On como empresa data-driven e transparente, caso certos dados agregados sejam expostos ao público ou clientes
GitHub
.
Notificações Inteligentes (Alertas Proativos): Incorporar um módulo de alertas que monitore continuamente os dados e notifique automaticamente eventos de interesse. Exemplos: alerta para o gestor quando uma determinada região ultrapassar certo limiar de DIC (indicando problema crônico de qualidade), ou notificação se surgir um cliente com consumo muito acima do típico (podendo indicar oportunidade para produto de eficiência energética). As notificações seriam enviadas via e-mail, SMS ou dentro do próprio painel, configuráveis conforme critérios estabelecidos pelos usuários. Esse recurso tornaria a plataforma proativa, chamando a atenção do usuário mesmo quando ele não estiver consultando ativamente os dashboards.
Segmentação Automática de Mercado: Utilizando algoritmos de clustering (como k-means, DBSCAN ou redes neurais SOM), a plataforma poderá segmentar o universo de unidades consumidoras em grupos com padrões similares. Essa segmentação poderia levar em conta perfil de carga, comportamento de consumo, localização geográfica e perfil econômico. O resultado seriam segmentos como “Grandes indústrias sazonais”, “Comércios urbanos com baixo fator de carga”, “Residenciais de alto consumo”, etc. Cada segmento receberia um rótulo e métricas agregadas, auxiliando a You.On a personalizar estratégias para cada grupo (ofertas específicas, campanhas regionais, etc). Essa funcionalidade de clusterização geográfica e de consumo já está no radar da equipe de dados
GitHub
 e promete extrair valor do grande volume de dados identificando padrões invisíveis a olho nu.
Inferência de Perfil Econômico e Social: Cruzar a base de leads com dados públicos socioeconômicos para enriquecer ainda mais o entendimento de cada unidade consumidora. Por exemplo, integrar informações do censo (IBGE) sobre renda média ou IDH do bairro/município de cada UC, ou ainda usar a razão social/CNPJ para obter detalhes da empresa (porte, faturamento estimado via fontes públicas). Com esse cruzamento, seria possível inferir características não explicitamente disponíveis: se uma unidade está em região de baixa renda mas com alto consumo, pode indicar ineficiência ou perdas; se uma empresa tem CNAE de “supermercado” mas está em área rural, pode indicar oportunidade de expansão local etc. Fontes como dados populacionais por setor censitário, ou mesmo APIs de geocoding (Nominatim, Google) para obter o endereço aproximado e contexto do ponto, podem ser empregadas. O sonho é que, combinando dados elétricos com dados econômicos, o You.On Intelligence forneça uma visão 360º de cada lead – não só quanto consome energia, mas qual o perfil daquele consumidor dentro da sociedade e economia, permitindo decisões mais informadas e segmentações mais precisas.
Em resumo, a visão futura do projeto é evoluir de uma excelente base de dados para uma plataforma de inteligência ativa e preditiva, agregando camadas de análise avançada, automação e integração. Cada um dos pontos acima representa um passo em direção a um sistema capaz de antecipar necessidades, otimizar operações e gerar valor de negócio diretamente a partir dos dados, consolidando a You.On como líder inovadora no mercado de energia.
Glossário Final e Licenciamento
Para alinhamento entre equipes técnicas e stakeholders de negócio, listamos abaixo um glossário com os principais termos técnicos e setoriais utilizados no projeto, bem como seus significados:
Termo	Definição
UC (Unidade Consumidora)	Instalação/fonte de consumo de energia elétrica identificada por um código único (ex: um cliente, medidor ou ponto de entrega)
GitHub
.
PAC (Potência Ativa Contratada)	Demanda de potência (kW) contratada pelo cliente junto à distribuidora para sua UC – indica o nível de carga acordada e disponibilizada
GitHub
.
DIC/FIC	Indicadores de qualidade de fornecimento: DIC = Duração de Interrupção por Unidade Consumidora (total de horas sem energia), FIC = Frequência de Interrupção por UC (número de desligamentos). São monitorados mensal e anualmente para avaliar a continuidade do serviço
GitHub
.
CNAE	Classificação Nacional de Atividades Econômicas – código oficial que identifica a atividade econômica de uma empresa (ex: comércio varejista de alimentos, fabricação de produtos têxteis). Usado para inferir o segmento de mercado de uma UC empresarial
GitHub
.
Ponto Notável	Ponto físico de referência na rede elétrica (por ex., conexão em transformador, barramento de subestação, etc.) associado a uma UC. Possui coordenadas geográficas conhecidas e é utilizado como fallback para localização quando a coordenada exata da UC não é disponível
GitHub
.
Camada (de dados)	No contexto ANEEL, refere-se a uma categoria de dados dentro da BDGD, normalmente separada por nível de tensão. Exemplos: UCAT (camada de unidades de alta tensão), UCMT (média tensão), UCBT (baixa tensão). Cada camada corresponde a um conjunto de dados geográficos específico dentro do SIG-R
GitHub
.
BDGD	Base de Dados Geográfica da Distribuidora – banco de dados geoespacial padronizado pela ANEEL (parte integrante do SIG-R) que representa, de forma simplificada, o sistema elétrico de cada distribuidora. Contém entidades como unidades consumidoras, redes, transformadores, etc., com atualização anual obrigatória
dadosabertos.aneel.gov.br
dadosabertos.aneel.gov.br
.
SIG-R	Sistema de Informação Geográfico Regulatório – plataforma regulatória da ANEEL que agrega as BDGDs de todas as distribuidoras, seguindo um modelo de dados unificado (DDA – Dicionário de Dados ANEEL). Serve para fiscalização e análises comparativas, padronizando entidades e atributos do setor elétrico
dadosabertos.aneel.gov.br
.
CCEE	Câmara de Comercialização de Energia Elétrica – entidade responsável pelo mercado de compra e venda de energia no Brasil. Disponibiliza dados abertos sobre consumo e geração no mercado livre, preços e estatísticas que podem ser integrados ao projeto para análises de mercado.
ANEEL	Agência Nacional de Energia Elétrica – órgão regulador do setor elétrico brasileiro, responsável por normatizar, fiscalizar concessionárias e manter bases de dados públicos (como a BDGD, séries de qualidade, tarifas, etc).

Licenciamento: Os dados de entrada utilizados pelo You.On Intelligence, em especial os conjuntos abertos da ANEEL (como a BDGD), estão licenciados sob formatos de dados abertos – por exemplo, a BDGD é disponibilizada sob a licença Open Data Commons ODbL (Open Database License)
dadosabertos.aneel.gov.br
, permitindo seu uso, compartilhamento e adaptação mediante atribuição. Por sua vez, todo o código-fonte e a base de dados consolidada do projeto são, até o momento, de uso interno e proprietários da You.On. Isso significa que seu acesso e distribuição são restritos conforme as políticas da empresa, exceto quando explicitamente definido o contrário. Em caso de compartilhamento de insights ou partes da base com terceiros, deve-se garantir conformidade com os termos de uso das fontes originais (por exemplo, mantendo a atribuição à ANEEL para dados originados de lá) e com as diretrizes de confidencialidade da You.On. Em resumo, incentivamos o uso responsável dos dados – aproveitando o poder dos dados abertos do setor elétrico – porém sempre respeitando licenças e normas vigentes para proteger tanto os direitos públicos quanto os interesses da empresa.