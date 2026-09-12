import os
import time
import requests
import duckdb
import pandas as pd

from databricks import sql

from datetime import date, datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.online.estacio.br"

USERNAME = os.getenv("ATLAS_USERNAME")
PASSWORD = os.getenv("ATLAS_PASSWORD")

SHAREPOINT_PATH = (
    r"C:\Users\joao.maciel\OneDrive - Corporativo"
    r"\Pós e Novos Produtos - Bases\ATLAS\Cursos Livres"
)

HOST = (
    "adb-2998601209865227.7.azuredatabricks.net"
)

HTTP_PATH = (
    "/sql/1.0/warehouses/59556454aa38ba1a"
)


def realizar_login(exibir_mensagem=False):

    if exibir_mensagem:
        print("Realizando login...")

    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )

    response.raise_for_status()

    token = response.json()["token"]

    if exibir_mensagem:
        print("Login realizado com sucesso!")

    return token


def criar_relatorio(token, data_inicio, data_fim):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "kind": "sales_orders",
        "inputs": {
            "by_range_date": [
                data_inicio,
                data_fim
            ]
        }
    }

    print("\nCriando relatório...")

    response = requests.post(
        f"{BASE_URL}/admin/reports",
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    report = response.json()

    print(f"REPORT_ID: {report['id']}")

    return report["id"]


def consultar_relatorio(token, report_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/admin/reports/{report_id}",
        headers=headers
    )

    response.raise_for_status()

    return response.json()


def aguardar_conclusao(report_id):

    inicio_processamento = time.time()

    mensagem_processamento_exibida = False

    while True:

        token = realizar_login()

        try:

            report_data = consultar_relatorio(
                token,
                report_id
            )

            status = report_data.get("status")

            if (
                status == "processing"
                and not mensagem_processamento_exibida
            ):
                print("\nRelatório em processamento...")
                mensagem_processamento_exibida = True

            if status in ["processed", "completed"]:

                tempo_processamento = round(
                    (time.time() - inicio_processamento) / 60,
                    2
                )

                print("\n========================")
                print("RELATÓRIO CONCLUÍDO")
                print("========================")
                print(
                    f"Tempo de processamento: "
                    f"{tempo_processamento} minutos\n"
                )

                return (
                    report_data,
                    token,
                    tempo_processamento
                    )

            if status in ["failed", "error"]:

                raise Exception(
                    f"Relatório falhou: {report_data}"
                )

        except requests.exceptions.HTTPError as erro:

            if erro.response.status_code == 401:
                continue

            raise

        time.sleep(10)


def obter_url_download(token, file_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/public/reports/files/{file_id}/download",
        headers=headers
    )

    response.raise_for_status()

    return response.json()["url"]


def baixar_csv(download_url, nome_arquivo):

    os.makedirs(
        SHAREPOINT_PATH,
        exist_ok=True
    )

    caminho = os.path.join(
        SHAREPOINT_PATH,
        nome_arquivo
    )

    response = requests.get(download_url)

    response.raise_for_status()

    with open(caminho, "wb") as arquivo:
        arquivo.write(response.content)

    print(f"Arquivo salvo em: {caminho}")

    return caminho


def atualizar_duckdb(nome_arquivo):

    caminho_csv = os.path.join(
        SHAREPOINT_PATH,
        nome_arquivo
    )

    conn = duckdb.connect("atlas.duckdb")

    conn.execute(f"""
        CREATE OR REPLACE TABLE vendas AS
        SELECT *
        FROM read_csv_auto(
            '{caminho_csv}',
            delim=';',
            all_varchar=true,
            strict_mode=false
        )
    """)

    conn.close()

    print("Tabela vendas atualizada no DuckDB!")

def registrar_log(
    report_id,
    file_id,
    nome_arquivo,
    data_inicio,
    data_fim,
    tempo_processamento,
    tempo_total
):

    os.makedirs("logs", exist_ok=True)

    caminho_log = os.path.join(
        "logs",
        "execucao.log"
    )

    data_execucao = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        caminho_log,
        "a",
        encoding="utf-8-sig"
    ) as arquivo:

        arquivo.write("\n")
        arquivo.write("=" * 80)
        arquivo.write("\n")

        arquivo.write(
            f"Data Execução: {data_execucao}\n"
        )

        arquivo.write(
            f"Período: {data_inicio} até {data_fim}\n"
        )

        arquivo.write(
            f"REPORT_ID: {report_id}\n"
        )

        arquivo.write(
            f"FILE_ID: {file_id}\n"
        )

        arquivo.write(
            f"Arquivo: {nome_arquivo}\n"
        )

        arquivo.write(
            f"Tempo Processamento: {tempo_processamento} minutos\n"
        )

        arquivo.write(
            f"Tempo Total: {tempo_total} minutos\n"
        )

        arquivo.write(
            "Status: SUCESSO\n"
        )

    print("Log gravado com sucesso!")



def atualizar_consolidado(
    caminho_incremental
):

    caminho_consolidado = os.path.join(
        SHAREPOINT_PATH,
        "vendas_consolidado.csv"
    )

    data_carga = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    df_incremental = pd.read_csv(
        caminho_incremental,
        sep=";",
        dtype=str,
        encoding="utf-8-sig"
    )



    df_incremental[
    "Código Transação Gateway"
    ] = (
    df_incremental[
        "Código Transação Gateway"
    ]
    .fillna("")
    .astype(str)
    )


    print(
    f"Gateways preenchidos: "
    f"{(df_incremental['Código Transação Gateway'].fillna('').str.strip() != '').sum():,}"
    )


    df_incremental["CHAVE_VENDA"] = (
    df_incremental["Número do Pedido"].astype(str)
    + "|"
    + df_incremental["Id Aluno"].astype(str)
    + "|"
    + df_incremental["Produto"].astype(str)
    )


    
    df_incremental["Data Carga"] = pd.to_datetime(
    data_carga,
    dayfirst=True
    )

    if not os.path.exists(
        caminho_consolidado
    ):

        

        df_incremental.to_csv(
            caminho_consolidado,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )

        print(
            "Consolidado criado."
        )

        return df_incremental

    df_consolidado = pd.read_csv(
        caminho_consolidado,
        sep=";",
        dtype=str,
        encoding="utf-8-sig"
    )

    df_consolidado["Data Carga"] = pd.to_datetime(
    df_consolidado["Data Carga"],
    errors="coerce"
    )

    df_consolidado["CHAVE_VENDA"] = (
    df_consolidado["Número do Pedido"].astype(str)
    + "|"
    + df_consolidado["Id Aluno"].astype(str)
    + "|"
    + df_consolidado["Produto"].astype(str)
    )


    df_consolidado[
    "Código Transação Gateway"
    ] = (
    df_consolidado[
        "Código Transação Gateway"
    ]
    .fillna("")
    .astype(str)
    )

    df_incremental["CHAVE_VENDA"] = (
        df_incremental["Número do Pedido"].astype(str)
        + "|"
        + df_incremental["Id Aluno"].astype(str)
        + "|"
        + df_incremental["Produto"].astype(str)
    )

    chaves_incrementais = set(
        df_incremental["CHAVE_VENDA"]
    )

    df_consolidado = df_consolidado[
        ~df_consolidado["CHAVE_VENDA"].isin(
            chaves_incrementais
        )
    ]


    df_final = pd.concat(
        [
        df_consolidado,
        df_incremental
        ],
        ignore_index=True
    )



    print(f"Antes da deduplicação: {len(df_final):,}")
    print(f"CHAVES únicas: {df_final['CHAVE_VENDA'].nunique():,}")

    df_final["Data Carga"] = pd.to_datetime(
        df_final["Data Carga"],
        dayfirst=True,
        errors="coerce"
    )
  

    duplicados = (
    df_final[
        df_final.duplicated(
            subset=["CHAVE_VENDA"],
            keep=False
        )
    ]
)

    print(
    f"Duplicados encontrados: "
    f"{len(duplicados):,}"
    )


    df_final["GATEWAY_PREENCHIDO"] = (
    df_final["Código Transação Gateway"]
    .fillna("")
    .str.strip()
    .ne("")
    )
    

    df_final = (
        df_final
         .sort_values(
        [
            "CHAVE_VENDA",
            "GATEWAY_PREENCHIDO",
            "Data Carga"
        ],
        ascending=[
            True,
            True,
            True
        ]
    )
    .drop_duplicates(
        subset=["CHAVE_VENDA"],
        keep="last"
    )
)

    df_final = df_final.drop(
        columns=["GATEWAY_PREENCHIDO"]
    )
    

    def corrigir_gateway(valor):

        if pd.isna(valor):
            return ""

        texto = str(valor).strip()

        if "E+" in texto.upper():
            try:
                return str(int(float(texto.replace(",", "."))))
            except:
                 return texto

        return texto

    df_final["Código Transação Gateway"] = (
        df_final["Código Transação Gateway"]
    .apply(corrigir_gateway)
    )



    df_final.to_csv(
        caminho_consolidado,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    df_incremental = (
    df_incremental
    .sort_values(
        "Data Carga"
    )
    .drop_duplicates(
        subset=["CHAVE_VENDA"],
        keep="last"
    )
    )

    print(
    f"Incremental após deduplicação: {len(df_incremental):,}"
    )

    print(
    f"Chaves únicas: "
    f"{df_incremental['CHAVE_VENDA'].nunique():,}"
    )

    return df_incremental
    

def publicar_silver_databricks(df):

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

    df["data_criacao"] = pd.to_datetime(
        df["data_criacao"],
        dayfirst=True,
        format="mixed",
        errors="coerce"
    )

    df["data_carga"] = pd.to_datetime(
        df["data_carga"],
        errors="coerce"
    )

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

    df = df.where(
        pd.notnull(df),
        None
    )

    print(
        f"\nRegistros para carga: {len(df):,}"
    )

    with sql.connect(
        server_hostname=HOST,
        http_path=HTTP_PATH,
        auth_type="databricks-cli"
    ) as connection:

        with connection.cursor() as cursor:

            chaves = (
                df["chave_venda"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            print(
                f"Chaves para atualizar: {len(chaves):,}"
            )

            for inicio in range(
                0,
                len(chaves),
                500
            ):

                lote = chaves[
                    inicio:inicio + 500
                ]

                valores = ",".join(
                    f"'{c}'"
                    for c in lote
                )

                cursor.execute(f"""
                DELETE FROM
                dev_novosnegocios.atlas.vendas_cursos_livres
                WHERE chave_venda IN (
                    {valores}
                )
                """)

            colunas = ",".join(df.columns)

            BATCH_SIZE = 500

            total = len(df)

            print(
                f"\nIniciando carga de {total:,} registros..."
            )

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
                                f"TIMESTAMP '{valor.strftime('%Y-%m-%d %H:%M:%S')}'"
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
                f"\n{total:,} registros processados."
            )

            cursor.execute("""
            SELECT COUNT(*)
            FROM dev_novosnegocios.atlas.vendas_cursos_livres
            """)

            resultado = cursor.fetchall()

            print(
            f"Total Silver: {resultado[0],}"
            )

    print(
        "\nCarga concluída com sucesso!"
    )

                    

def main():

    inicio_execucao = time.time()

    token = realizar_login(exibir_mensagem=True)

    hoje = date.today()

    data_inicio = (
    hoje - timedelta(days=31)
    ).strftime("%Y-%m-%d")

    data_fim = hoje.strftime("%Y-%m-%d")

    print(
        f"\nPeríodo selecionado: "
        f"{data_inicio} até {data_fim}"
    )

    report_id = criar_relatorio(
        token=token,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    report_final, token, tempo_processamento = (
            aguardar_conclusao(
                report_id
        )
    )

    arquivo = report_final["files"][0]

    file_id = arquivo["id"]

    nome_arquivo = (
        f"vendas_cursos_livres_"
        f"{data_inicio}_"
        f"{data_fim}.csv"
    )


    download_url = obter_url_download(
        token,
        file_id
    )

    caminho_csv = baixar_csv(
    download_url,
    nome_arquivo
    )


    df_final = atualizar_consolidado(
    caminho_csv
    )

    publicar_silver_databricks(
    df_final
    )



    atualizar_duckdb(
    "vendas_consolidado.csv"
    )  

    # Remove o arquivo incremental
    if os.path.exists(caminho_csv):

        os.remove(caminho_csv)

        print("Arquivo incremental removido.")

    tempo_total = round(
    (time.time() - inicio_execucao) / 60,
    2
)

    registrar_log(
    report_id,
    file_id,
    nome_arquivo,
    data_inicio,
    data_fim,
    tempo_processamento,
    tempo_total
)

        

    print("\n========================")
    print("PROCESSO CONCLUÍDO")
    print("========================")
    print(
        f"Tempo total da execução: "
        f"{tempo_total} minutos"
    )


if __name__ == "__main__":
    main()