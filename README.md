# Plataforma de Dados para Validação de Clientes em PDV — V2

O projeto implementa uma **plataforma de dados completa para validação de clientes no momento da venda (PDV)**, utilizando práticas modernas de Engenharia de Dados: ingestão automatizada, transformação analítica, data warehouse em nuvem, cache de baixa latência e API desacoplada.

Ele é a **evolução ferramental da versão 1** do projeto:
👉 https://github.com/ojoseafonso/promo-clube-pdv-v1.git

---

## 🎯 Contexto e Motivação

A versão inicial do projeto (V1) foi construída para validar uma ideia: garantir que dados recém criados estivessem disponíveis para consumo operacional com baixa latência. 
Para isso, utilizei uma stack mais simples Faker básico, Docker, PostgreSQL, DLT, Redis e FastAPI, com foco apenas em provar o fluxo e o conceito.

Com o amadurecimento da solução consegui conectar ferramentas consegui evoluir a arquitetura para incorporar elementos comuns em Modern Data Stack:

* Separação clara entre dados RAW e dados transformados

* Uso de um Data Warehouse analítico em nuvem (Snowflake)

* Camada de transformação com dbt

* Ingestão incremental via CDC no Airbyte

* Arquitetura orientada a serviços

Essa evolução foi influenciada por estudos recentes em Engenharia de Dados, mas o objetivo principal permaneceu o mesmo, mostrar que ferramentas são meios e o foco está em resolver problemas reais de dados com clareza, escalabilidade e consistência.

## 🏗️ Arquitetura da Solução

<img width="1738" height="475" alt="projeto_v2" src="https://github.com/user-attachments/assets/d688c399-d2d8-4a99-bf34-10161e54aa3f" />

**Todos os componentes da plataforma são executados via Docker Compose, com exceção do Snowflake, que atua como Data Warehouse gerenciado em nuvem.**

## 🛠️ Stack Tecnológico
Camada|Ferramenta|Função
|--------|-----------|------|
Geração de Dados|Faker|Simulação de cadastros realistas
OLTP|PostgreSQL|Sistema transacional
Ingestão|Airbyte (CDC)|Captura incremental de dados
Warehouse|Snowflake|Camada RAW e analítica
Transformação|dbt|Staging e modelos dimensionais
Cache|Redis|Consulta de baixa latência
API|FastAPI|Serviço para PDV
Infra|Docker Compose|Orquestração local

## 🔄 Fluxo de Dados Detalhado
1️⃣ Simulação do Sistema Transacional

Serviço Python gera cadastros contínuos

Campos incluem:

status do clube

opt-in marketing

ticket médio estimado

origem de campanha

Dados são inseridos no PostgreSQL (OLTP)

2️⃣ CDC com Airbyte

Airbyte monitora alterações no PostgreSQL

Captura incremental via CDC

Carrega dados no Snowflake (RAW)

📌 Resultado:
Sem cargas completas e sem impacto no banco transacional.

3️⃣ Transformações com dbt

Modelos de staging (stg_clientes_clube)

Modelo dimensional (dim_clientes_clube)

Regras de negócio aplicadas:

clientes ativos no clube

campos mínimos para validação no PDV

4️⃣ Cache de Baixa Latência

Serviço Python consulta o Snowflake

Dados prontos são carregados no Redis

Estrutura chave-valor otimizada para leitura

5️⃣ API de Consumo (PDV)

API consulta exclusivamente o Redis

Nenhuma dependência direta de banco

Respostas previsíveis e rápidas

