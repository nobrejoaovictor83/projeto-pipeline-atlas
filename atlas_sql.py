import sys
import duckdb

query = sys.argv[1]

conn = duckdb.connect("atlas.duckdb")

with open(
    f"sql/{query}.sql",
    "r",
    encoding="utf-8"
) as arquivo:

    sql = arquivo.read()

resultado = conn.execute(sql).fetchdf()

print(resultado)

conn.close()