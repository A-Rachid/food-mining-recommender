"""
mining.py
---------
Data Mining — Règles d'association sur commandes restaurant (Zomato / Delhi NCR)
Méthode : Apriori (mlxtend)

Utilisation :
    python mining.py                          → analyse complète avec affichage console
    from mining import load_transactions, run_apriori, get_recommendations
"""

import re
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


# ─────────────────────────────────────────────
# 1. CHARGEMENT ET PARSING DES TRANSACTIONS
# ─────────────────────────────────────────────

def parse_items(raw: str) -> list[str]:
    """
    Extrait les noms de produits depuis une chaîne du type :
        '1 x Bageecha Pizza, 2 x Cheesy Garlic Bread'
    → ['Bageecha Pizza', 'Cheesy Garlic Bread']
    """
    if pd.isna(raw):
        return []
    items = re.findall(r"\d+ x (.+?)(?:,|$)", str(raw))
    return [item.strip() for item in items]


def load_transactions(filepath: str, multi_items_only: bool = True) -> tuple[pd.DataFrame, list[list[str]]]:
    """
    Charge le CSV et retourne :
        - df         : DataFrame complet enrichi
        - transactions : liste de listes d'items (une liste par commande)

    Paramètres
    ----------
    filepath         : chemin vers le fichier CSV
    multi_items_only : si True, ne conserve que les commandes avec 2+ articles
                       (recommandé pour la qualité des règles d'association)
    """
    df = pd.read_csv(filepath)

    # Parsing de la colonne 'Items in order'
    df["items_list"] = df["Items in order"].apply(parse_items)
    df["nb_items"]   = df["items_list"].apply(len)

    if multi_items_only:
        df = df[df["nb_items"] >= 2].reset_index(drop=True)

    transactions = df["items_list"].tolist()
    return df, transactions


# ─────────────────────────────────────────────
# 2. ENCODAGE + APRIORI
# ─────────────────────────────────────────────

def encode_transactions(transactions: list[list[str]]) -> pd.DataFrame:
    """
    Transforme la liste de transactions en matrice binaire (one-hot)
    requise par mlxtend.
    """
    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    return pd.DataFrame(te_array, columns=te.columns_)


def run_apriori(
    transactions: list[list[str]],
    min_support: float = 0.01,
    min_confidence: float = 0.05,
    min_lift: float = 1.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Exécute l'algorithme Apriori et retourne les règles d'association.

    Paramètres
    ----------
    transactions   : liste de listes d'items
    min_support    : fréquence minimale d'apparition d'un itemset (0–1)
    min_confidence : probabilité minimale de la règle antécédent → conséquent (0–1)
    min_lift       : lift minimum (1.0 = pas de corrélation, >1 = corrélation positive)

    Retourne
    --------
    frequent_itemsets : DataFrame des itemsets fréquents avec leur support
    rules             : DataFrame des règles triées par lift décroissant
    """
    df_encoded = encode_transactions(transactions)

    # Extraction des itemsets fréquents
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
    frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(len)

    # Génération des règles
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)

    # Filtre sur la confiance
    rules = rules[rules["confidence"] >= min_confidence].copy()

    # Conversion frozenset → string lisible
    rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(list(x))))
    rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(sorted(list(x))))

    # Colonnes utiles + tri
    cols = ["antecedents", "consequents", "support", "confidence", "lift", "leverage", "conviction"]
    rules = rules[cols].sort_values("lift", ascending=False).reset_index(drop=True)

    return frequent_itemsets, rules


# ─────────────────────────────────────────────
# 3. MOTEUR DE RECOMMANDATION
# ─────────────────────────────────────────────

def get_recommendations(
    item: str,
    rules: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Retourne les produits les plus souvent associés à un item donné.

    Paramètres
    ----------
    item   : nom du produit sélectionné (doit correspondre exactement au nom dans les règles)
    rules  : DataFrame des règles générées par run_apriori()
    top_n  : nombre de recommandations à retourner

    Retourne
    --------
    DataFrame avec les colonnes : produit_recommandé, confiance, lift
    """
    mask = rules["antecedents"].str.contains(re.escape(item), case=False, na=False)
    matched = rules[mask].copy()

    if matched.empty:
        return pd.DataFrame(columns=["produit_recommandé", "confiance", "lift"])

    matched = matched.rename(columns={"consequents": "produit_recommandé", "confidence": "confiance"})
    return (
        matched[["produit_recommandé", "confiance", "lift"]]
        .sort_values("lift", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


# ─────────────────────────────────────────────
# 4. STATISTIQUES EXPLORATOIRES
# ─────────────────────────────────────────────

def get_stats(df: pd.DataFrame, transactions: list[list[str]]) -> dict:
    """
    Retourne un dictionnaire de statistiques utiles pour le dashboard.
    """
    all_items = [item for basket in transactions for item in basket]
    item_counts = pd.Series(all_items).value_counts()

    stats = {
        "nb_commandes_total"  : len(df),
        "nb_commandes_multi"  : df[df["nb_items"] >= 2].shape[0],
        "nb_items_uniques"    : len(item_counts),
        "nb_restaurants"      : df["Restaurant name"].nunique(),
        "top_items"           : item_counts.head(10),
        "items_par_commande"  : df["nb_items"].describe(),
        "restaurants"         : df["Restaurant name"].value_counts(),
    }
    return stats


# ─────────────────────────────────────────────
# 5. POINT D'ENTRÉE — DEMO CONSOLE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    DATA_PATH = "data/order_history.csv"

    print("=" * 60)
    print("  DATA MINING — Recommandation de plats (Apriori)")
    print("=" * 60)

    # Chargement
    print("\n[1/4] Chargement des données...")
    df, transactions = load_transactions(DATA_PATH, multi_items_only=True)
    stats = get_stats(df, transactions)

    print(f"      ✓ {stats['nb_commandes_total']:,} commandes chargées")
    print(f"      ✓ {stats['nb_commandes_multi']:,} commandes avec 2+ articles")
    print(f"      ✓ {stats['nb_items_uniques']} produits uniques")
    print(f"      ✓ {stats['nb_restaurants']} restaurants")

    # Apriori
    print("\n[2/4] Exécution de l'algorithme Apriori...")
    frequent_itemsets, rules = run_apriori(
        transactions,
        min_support=0.01,
        min_confidence=0.05,
        min_lift=1.0,
    )
    print(f"      ✓ {len(frequent_itemsets)} itemsets fréquents trouvés")
    print(f"      ✓ {len(rules)} règles d'association générées")

    # Top règles
    print("\n[3/4] Top 10 règles par lift :")
    print("-" * 60)
    for _, row in rules.head(10).iterrows():
        print(f"  [{row['antecedents']}]")
        print(f"    → {row['consequents']}")
        print(f"       support={row['support']:.3f} | confiance={row['confidence']:.2%} | lift={row['lift']:.2f}")
        print()

    # Exemple de recommandation
    test_item = "Bageecha Pizza"
    print(f"\n[4/4] Recommandations pour '{test_item}' :")
    print("-" * 60)
    reco = get_recommendations(test_item, rules, top_n=5)
    if reco.empty:
        print("  Aucune recommandation trouvée.")
    else:
        for _, row in reco.iterrows():
            print(f"  → {row['produit_recommandé']}  (confiance: {row['confiance']:.2%}, lift: {row['lift']:.2f})")

    print("\n" + "=" * 60)
    print("  Analyse terminée. Lancez app.py pour le dashboard.")
    print("=" * 60)
