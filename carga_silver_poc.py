import pandas as pd
from databricks import sql

ARQUIVO = (
    r"C:\Users\joao.maciel\OneDrive - Corporativo"
    r"\Pós e Novos Produtos - Bases\ATLAS"
    r"\Cursos Livres\vendas_consolidado.csv"
)

HOST = (
    "adb-2998601209865227.7.azuredatabricks.net"
)

HTTP_PATH = (
    "/sql/1.0/warehouses/59556454aa38ba1a"
)

# ==========================================
# LEITURA
# ==========================================

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    dtype=str,
    encoding="utf-8-sig"
)

print(
    f"Registros lidos: {len(df):,}"
)

# ==========================================
# POC COM 10 REGISTROS MAIS RECENTES
# ==========================================

df["Data Carga"] = pd.to_datetime(
    df["Data Carga"],
    dayfirst=True,
    errors="coerce"
)

df = (
    df.sort_values(
        "Data Carga",
        ascending=False
    )
)


# ==========================================
# RENOMEAÇÃO
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

print(len(df))
print(df["chave_venda"].nunique())

print("\nGateway após rename:")

print(
    df[
        [
            "numero_pedido",
            "codigo_transacao_gateway"
        ]
    ]
    .loc[
        df["codigo_transacao_gateway"].notna()
    ]
    .head(20)
)

print("\nColunas Silver:")
print(df.columns.tolist())

print(
    f"\nRegistros para carga: {len(df)}"
)


# ==========================================
# CONVERSÃO DE DATAS
# ==========================================

df["data_criacao"] = pd.to_datetime(
    df["data_criacao"],
    dayfirst=True,
    format="mixed",
    errors="coerce"
)

print(
    "\nDatas nulas após conversão:",
    df["data_criacao"].isna().sum()
)

df["data_carga"] = pd.to_datetime(
    df["data_carga"],
    errors="coerce"
)

print(
    "\nDatas nulas após conversão:",
    df["data_criacao"].isna().sum()
)

print(
    df["data_criacao"]
    .dropna()
    .head(20)
)

print(
    df["data_criacao"]
    .astype(str)
    .head(20)
)


# ==========================================
# CONVERSÃO DE VALORES
# ==========================================

df["valor_desconto"] = pd.to_numeric(
    df["valor_desconto"],
    errors="coerce"
)

df["valor_pago"] = pd.to_numeric(
    df["valor_pago"]
    .astype(str)
    .str.replace(",", ".", regex=False),
    errors="coerce"
)

# ==========================================
# NAN -> NULL
# ==========================================

df = df.where(
    pd.notnull(df),
    None
)

print(
    df[
        [
            "codigo_transacao_gateway"
        ]
    ]
    .dropna()
    .head(20)
)

print(
    df["codigo_transacao_gateway"].dtype
)

# ==========================================
# CARGA
# ==========================================

print(
    "\nDatas nulas:",
    df["data_criacao"].isna().sum()
)

print(
    "\nTotal registros:",
    len(df)
)

print(
    "\nChaves únicas:",
    df["chave_venda"].nunique()
)


with sql.connect(
    server_hostname=HOST,
    http_path=HTTP_PATH,
    auth_type="databricks-cli"
) as connection:

    with connection.cursor() as cursor:

        cursor.execute("""
        TRUNCATE TABLE
        dev_novosnegocios.atlas.vendas_cursos_livres
        """)

        print("\nTabela limpa.")

        colunas = ",".join(df.columns)

        BATCH_SIZE = 500

        total = len(df)

        for inicio in range(
            0,
            total,
            BATCH_SIZE
        ):

            fim = min(
                inicio + BATCH_SIZE,
                total
            )

            df_lote = df.iloc[
                inicio:fim
            ]

            print(
                f"\nProcessando lote "
                f"{inicio + 1:,} até "
                f"{fim:,} de {total:,}"
            )

            valores_lote = []

            for _, row in df_lote.iterrows():

                valores = []

                for valor in row:

                    if (
                        valor is None
                        or pd.isna(valor)
                    ):

                        valores.append(
                            "NULL"
                        )

                    elif isinstance(
                        valor,
                        pd.Timestamp
                    ):

                        valores.append(
                            f"TIMESTAMP "
                            f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'"
                        )

                    elif isinstance(
                        valor,
                        (float, int)
                    ):

                        valores.append(
                            str(valor)
                        )

                    else:

                        valor = str(
                            valor
                        ).replace(
                            "'",
                            "''"
                        )

                        valores.append(
                            f"'{valor}'"
                        )

                valores_lote.append(
                    f"({','.join(valores)})"
                )

            sql_insert = f"""
            INSERT INTO
            dev_novosnegocios.atlas.vendas_cursos_livres
            ({colunas})
            VALUES
            {','.join(valores_lote)}
            """

            cursor.execute(
                sql_insert
            )

            print(
                f"Lote concluído: "
                f"{fim:,}/{total:,}"
            )

        print(
            f"\n{total:,} registros processados."
        )

        cursor.execute("""
        SELECT COUNT(*)
        FROM dev_novosnegocios.atlas.vendas_cursos_livres
        """)

        resultado = cursor.fetchall()

        print("\nContagem final:")
        print(resultado)

print(
    "\nCarga concluída com sucesso!"
)