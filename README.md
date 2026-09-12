# projeto-pipeline-atlas
O Atlas Pipeline é uma solução de engenharia de dados desenvolvida para automatizar a coleta, tratamento, consolidação e disponibilização das vendas de Cursos Livres da plataforma Atlas. O processo elimina atividades manuais de extração e atualização de bases, garantindo maior confiabilidade, rastreabilidade e disponibilidade das informações para análises e tomada de decisão.

A aplicação realiza autenticação na API do Atlas, solicita a geração de relatórios de vendas por período e monitora o processamento até a conclusão. Após a disponibilização do relatório, o arquivo é baixado automaticamente e utilizado como fonte para atualização da base histórica consolidada.

Durante o tratamento dos dados, o pipeline aplica regras de padronização, corrige inconsistências, cria chaves de negócio para identificação única das vendas e remove registros duplicados, preservando sempre a versão mais atual e completa de cada transação. O histórico consolidado é armazenado em arquivo CSV para garantir persistência local e recuperação de informações.

Após o processamento, é executada uma carga incremental para o Databricks, atualizando apenas os registros impactados na execução. Para isso, o pipeline remove previamente as chaves de negócio existentes na camada analítica e insere os registros atualizados, reduzindo significativamente o volume de dados trafegado e o tempo de processamento.

Além da atualização do ambiente analítico no Databricks, o processo mantém uma cópia estruturada dos dados em DuckDB para consultas locais, análises exploratórias e validações operacionais. Ao final da execução, os arquivos temporários são removidos e um log detalhado é gerado contendo informações de auditoria, período processado, identificadores dos relatórios, tempo de execução e status da carga.
