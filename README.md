# projeto-pipeline-atlas
Pipeline automatizado para extração, tratamento e consolidação das vendas de Cursos Livres do Atlas. O processo consome relatórios via API, mantém um histórico consolidado, trata inconsistências e duplicidades por chave de negócio, realiza carga incremental no Databricks, atualiza o DuckDB e registra logs para auditoria e monitoramento contínuo.
