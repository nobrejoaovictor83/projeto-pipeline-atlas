import pandas as pd

ARQUIVO = r"C:\Users\joao.maciel\OneDrive - Corporativo\Pós e Novos Produtos - Bases\ATLAS\Cursos Livres\vendas_consolidado.csv"

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    dtype=str,
    encoding="utf-8-sig"
)

print("\nShape:")
print(df.shape)

print("\nColunas:")
for coluna in df.columns:
    print(coluna)