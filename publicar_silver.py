import pandas as pd

ARQUIVO = (
    r"C:\Users\joao.maciel\OneDrive - Corporativo"
    r"\Pós e Novos Produtos - Bases\ATLAS"
    r"\Cursos Livres\vendas_consolidado.csv"
)

# ==========================================
# LEITURA DO CSV
# ==========================================

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    dtype=str,
    encoding="utf-8-sig"
)

# ==========================================
# RENOMEAÇÃO DAS COLUNAS
# ==========================================

df = df.rename(columns={
    "Número do Pedido": "numero_pedido",
    "Status do Pedido": "status_pedido",
    "Data de Criação": "data_criacao",
    "Nome do Aluno": "nome_aluno",
    "E-mail do Aluno": "email_aluno",
    "Telefone do Aluno": "telefone_aluno",
    "CPF do Pagador": "cpf_pagador",
    "Código do Cupom": "codigo_cupom",
    "Tipo de Desconto": "tipo_desconto",
    "Valor do Desconto": "valor_desconto",
    "Valor Pago": "valor_pago",
    "Produto": "produto",
    "Estado do Pagador": "estado_pagador",
    "Nome do Estado do Pagador": "nome_estado_pagador",
    "Cidade do Pagador": "cidade_pagador",
    "Bairro do Pagador": "bairro_pagador",
    "Rua do Pagador": "rua_pagador",
    "Número do Pagador": "numero_pagador",
    "CEP do Pagador": "cep_pagador",
    "Meio de Pagamento": "meio_pagamento",
    "Código Transação Gateway": "codigo_transacao_gateway",
    "Categoria": "categoria",
    "Id Aluno": "id_aluno",
    "CHAVE_VENDA": "chave_venda",
    "Data Carga": "data_carga"
})

# ==========================================
# CONVERSÃO DE VALORES MONETÁRIOS
# ==========================================

for coluna in [
    "valor_desconto",
    "valor_pago"
]:
    df[coluna] = (
        df[coluna]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df[coluna] = pd.to_numeric(
        df[coluna],
        errors="coerce"
    )

# ==========================================
# CONVERSÃO DE DATAS
# ==========================================

colunas_data = [
    "data_criacao",
    "data_inclusao",
    "data_ultima_atualizacao",
    "data_atualizacao"
]

for coluna in colunas_data:

    df[coluna] = pd.to_datetime(
        df[coluna],
        dayfirst=True,
        errors="coerce"
    )

# ==========================================
# VALIDAÇÃO
# ==========================================

print("\nSHAPE")
print(df.shape)

print("\nTIPOS DAS COLUNAS")
print(df.dtypes)

print("\nAMOSTRA")
print(
    df[
        [
            "numero_pedido",
            "valor_pago",
            "data_criacao",
            "data_inclusao"
        ]
    ].head()
)