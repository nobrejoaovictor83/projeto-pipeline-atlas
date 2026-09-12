# Pipeline_Atlas
## 📌 Sobre o Projeto

O **Atlas Pipeline** é uma solução de **Engenharia de Dados** desenvolvida para automatizar o processo de coleta, tratamento, consolidação e disponibilização dos dados de vendas de **Cursos Livres** da plataforma Atlas.

O projeto foi criado com o objetivo de eliminar atividades manuais relacionadas à extração e atualização das bases de dados, proporcionando um processo mais **automatizado, confiável, rastreável e eficiente**.

A aplicação realiza a integração com a **API Atlas**, automatizando desde a solicitação dos relatórios de vendas até a atualização das bases analíticas utilizadas para análises e tomada de decisão.

---

## ⚙️ Como funciona

O pipeline executa um fluxo completo de processamento de dados:

1. 🔐 Realiza a autenticação automática na API Atlas.
2. 📊 Solicita a geração dos relatórios de vendas para o período informado.
3. ⏳ Monitora o processamento dos relatórios até sua conclusão.
4. 📥 Realiza o download automático dos arquivos CSV gerados.
5. 🧹 Trata, padroniza e corrige inconsistências nos dados.
6. 🔑 Cria uma chave única de negócio (`CHAVE_VENDA`) para identificação das transações.
7. 🔍 Identifica e remove registros duplicados, mantendo sempre a versão mais atual e completa das informações.
8. 📚 Consolida os dados em uma base histórica persistente.
9. ⚡ Executa uma carga incremental no Databricks, atualizando apenas os registros impactados.
10. 🦆 Mantém uma cópia estruturada dos dados em DuckDB para consultas locais e validações.
11. 📝 Gera logs detalhados para auditoria e monitoramento do processo.
12. 🗑️ Remove automaticamente os arquivos temporários gerados durante a execução.

---

## 🏗️ Arquitetura do Processo

```text
        ┌───────────────┐
        │   API Atlas   │
        └───────┬───────┘
                │
                ▼
      ┌─────────────────────┐
      │ Geração de Relatório│
      └─────────┬───────────┘
                │
                ▼
        ┌───────────────┐
        │   Download    │
        │     CSV       │
        └───────┬───────┘
                │
                ▼
     ┌───────────────────────┐
     │ Tratamento dos Dados  │
     │  • Padronização       │
     │  • CHAVE_VENDA        │
     │  • Deduplicação       │
     └───────────┬───────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ Histórico Consolidado│
      │        CSV          │
      └──────────┬──────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐  ┌────────────────┐
│   Databricks  │  │     DuckDB     │
│ Carga Incremental│ │ Consultas Locais│
└───────────────┘  └────────────────┘
```

---

## ✨ Principais Funcionalidades

* Autenticação automática na API Atlas.
* Geração e monitoramento de relatórios de vendas.
* Download automatizado de arquivos CSV.
* Consolidação histórica dos dados.
* Tratamento e padronização das informações.
* Criação de chave única de negócio (`CHAVE_VENDA`).
* Identificação e remoção de registros duplicados.
* Preservação dos registros mais recentes e completos.
* Carga incremental otimizada para o Databricks.
* Atualização de base local utilizando DuckDB.
* Geração de logs para auditoria e monitoramento.
* Limpeza automática de arquivos temporários.

---

## ⚡ Estratégia de Carga Incremental

Para otimizar o processo de atualização da camada analítica, o pipeline utiliza uma estratégia de **carga incremental baseada em chave de negócio**.

O processo funciona da seguinte forma:

* Identifica os registros impactados durante a execução.
* Remove previamente os registros existentes no Databricks utilizando a `CHAVE_VENDA`.
* Insere os registros atualizados na tabela analítica.

Essa abordagem reduz significativamente o volume de dados processados e trafegados durante as atualizações, proporcionando maior eficiência e melhor desempenho do pipeline.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia                   | Utilização                                      |
| ---------------------------- | ----------------------------------------------- |
| **Python**                   | Desenvolvimento e orquestração do pipeline      |
| **Pandas**                   | Manipulação e tratamento dos dados              |
| **Requests**                 | Comunicação com a API Atlas                     |
| **DuckDB**                   | Armazenamento e consultas locais                |
| **Databricks SQL Connector** | Integração com o Databricks                     |
| **Databricks SQL Warehouse** | Processamento e atualização da camada analítica |
| **API Atlas**                | Fonte dos relatórios de vendas                  |
| **CSV**                      | Persistência e consolidação histórica           |
| **Dotenv**                   | Gerenciamento de variáveis de ambiente          |

---

## 🔐 Segurança e Configurações

Informações sensíveis, como credenciais, tokens e configurações de conexão, são armazenadas utilizando **variáveis de ambiente**, evitando a exposição de dados confidenciais no código-fonte.

Essas informações não devem ser versionadas no repositório.

Exemplo:

```env
ATLAS_USER=seu_usuario
ATLAS_PASSWORD=sua_senha

DATABRICKS_SERVER_HOSTNAME=seu_host
DATABRICKS_HTTP_PATH=seu_http_path
DATABRICKS_ACCESS_TOKEN=seu_token
```

Recomenda-se utilizar um arquivo `.env` local e incluí-lo no `.gitignore`.

---

## 📊 Benefícios

* ⏱️ Redução de atividades manuais.
* 🤖 Automatização do processo de extração e atualização.
* 📈 Maior confiabilidade das informações.
* 🗂️ Histórico consolidado e rastreável.
* ⚡ Processamento incremental otimizado.
* 🔍 Facilidade para auditoria e validação dos dados.
* 📊 Base preparada para consumo em dashboards e análises.
* 🧠 Possibilidade de utilização em modelos e aplicações analíticas.
* 🛠️ Maior facilidade de manutenção e evolução do processo.

---

## 🎯 Objetivo

O **Atlas Pipeline** busca transformar um processo anteriormente dependente de atividades manuais em uma solução automatizada e estruturada de Engenharia de Dados.

Com isso, o projeto garante maior disponibilidade, confiabilidade e rastreabilidade das informações de vendas de Cursos Livres, criando uma base sólida para análises operacionais, indicadores de performance e tomada de decisão.

---

## 👨‍💻 Autor

**Victor Nobre**

Projeto desenvolvido como iniciativa de automação e engenharia de dados para otimização do processo de coleta, tratamento e disponibilização de dados de vendas.
