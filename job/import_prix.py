"""PriceWatch — job d'import (VERSION OPTIMISÉE : lecture par morceaux, opérations vectorisées).

Lit l'historique brut des relevés et calcule, pour chaque produit, magasin et mois
depuis 2020 : le prix minimum, maximum et moyen TTC, le prix moyen hors taxes
(TVA alimentaire à 5,5 %) et le nombre de relevés. Écrit le résultat dans out/monthly.csv.

Le job affiche ce qu'il a consommé à la fin : ne touchez pas au bloc « Mesures ».
"""
import resource
import time
from pathlib import Path

import pandas as pd

DATA_DIR = Path("/data") if Path("/data").exists() else Path(__file__).resolve().parent.parent / "data"
SRC = DATA_DIR / "raw" / "history.csv"
OUT = DATA_DIR / "out" / "monthly.csv"

start = time.perf_counter()

# 1. Lecture par morceaux, uniquement les colonnes utiles.
#    Pour chaque morceau on garde min, max, somme et nombre par groupe.
partiels = []
for chunk in pd.read_csv(
    SRC,
    usecols=["date", "shop", "product", "price"],
    dtype={"shop": "category", "product": "category"},
    chunksize=200_000,
):
    # 2. Mois et filtre depuis 2020 (opérations vectorisées, pas de apply)
    chunk["month"] = chunk["date"].str[:7]
    chunk = chunk[chunk["month"] >= "2020"]

    # 3. Prix hors taxes (vectorisé)
    chunk["price_ht"] = chunk["price"] / 1.055

    # 4. Agrégat partiel du morceau
    partiels.append(
        chunk.groupby(["product", "shop", "month"], observed=True)
        .agg(
            price_min=("price", "min"),
            price_max=("price", "max"),
            price_sum=("price", "sum"),
            price_ht_sum=("price_ht", "sum"),
            count=("price", "count"),
        )
    )

# 5. Recombinaison des morceaux
tous = pd.concat(partiels).reset_index()
result = (
    tous.groupby(["product", "shop", "month"], observed=True)
    .agg(
        price_min=("price_min", "min"),
        price_max=("price_max", "max"),
        price_sum=("price_sum", "sum"),
        price_ht_sum=("price_ht_sum", "sum"),
        count=("count", "sum"),
    )
    .reset_index()
)

# 6. Moyenne = somme / nombre (et non une moyenne de moyennes)
result["price_mean"] = result["price_sum"] / result["count"]
result["price_ht_mean"] = result["price_ht_sum"] / result["count"]
result = (
    result[["product", "shop", "month", "price_min", "price_max",
            "price_mean", "price_ht_mean", "count"]]
    .round(2)
    .sort_values(["product", "shop", "month"])
)

OUT.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUT, index=False)

# --- Mesures (ne pas modifier) -------------------------------------------------
wall = time.perf_counter() - start
usage = resource.getrusage(resource.RUSAGE_SELF)
cpu = usage.ru_utime + usage.ru_stime
print(f"Lignes écrites       : {len(result)}")
print(f"Temps réel           : {wall:6.1f} s")
print(f"Temps CPU (user+sys) : {cpu:6.1f} s  (ratio CPU / réel : {cpu / wall:.2f})")
print(f"Pic de RAM (RSS)     : {usage.ru_maxrss / 1024:6.0f} Mo")