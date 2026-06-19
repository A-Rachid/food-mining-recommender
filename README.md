# 🍽️ Food Mining — Recommandation de plats par analyse de paniers

> **Data Mining · Règles d'association · Dashboard interactif**  
> Analyse des commandes d'un service de livraison pour détecter quels plats sont commandés ensemble et générer des recommandations automatiques.

🔗 **[Voir le dashboard en ligne](https://ton-app.streamlit.app)** *(à mettre à jour après déploiement)*

---

## 📌 Contexte

Ce projet applique les techniques de **data mining** (algorithme Apriori) sur un dataset de commandes restaurant inspiré de la plateforme **Zomato (Delhi NCR)**.

L'objectif : identifier des **règles d'association** entre plats — *"les clients qui commandent X commandent aussi Y"* — et les rendre exploitables via un dashboard Streamlit interactif.

---

## 🎯 Ce que fait ce projet

- **Parse et nettoie** 22 000 commandes brutes au format texte
- **Encode les transactions** en matrice binaire (one-hot)
- **Exécute l'algorithme Apriori** pour extraire les itemsets fréquents et les règles d'association
- **Calcule les métriques clés** : support, confiance, lift, leverage, conviction
- **Recommande des plats** en temps réel selon le choix de l'utilisateur
- **Visualise les résultats** : heatmap de co-occurrences, scatter plot, règles filtrables
- **Mode clair / sombre** et **onglet glossaire** expliquant chaque métrique avec exemples chiffrés

---

## 📊 Dataset

> ⚠️ Le dataset original (Kaggle, Zomato Delhi NCR) ne peut pas être redistribué publiquement. Ce projet utilise donc un **dataset synthétique généré sur-mesure** (`generate_dataset.py`), reproduisant fidèlement la structure, les proportions et les comportements d'achat du dataset réel — sans contrainte de licence.

| Attribut | Valeur |
|---|---|
| Type | Synthétique, généré par script Python (`generate_dataset.py`) |
| Inspiré de | Zomato Order History — Delhi NCR |
| Période simulée | Septembre 2024 → Janvier 2025 |
| Commandes totales | 22 000 |
| Commandes multi-items | 12 348 |
| Restaurants | 6 |
| Produits uniques | 92 |

**Colonne clé :** `Items in order` au format `"1 x Bageecha Pizza, 1 x Makhani Paneer Pizza"` — parsée avec regex pour extraire les transactions.

**Reproductibilité :** le script `generate_dataset.py` recrée le dataset à l'identique (seed fixe) — aucune dépendance à un fichier externe, 100% libre de droits.

---

## 🔬 Méthodologie Data Mining

### Algorithme : Apriori

L'Apriori est un algorithme classique de **market basket analysis**. Il fonctionne en deux étapes :

1. **Extraction des itemsets fréquents** — trouve tous les groupes de produits qui apparaissent ensemble au-delà d'un seuil de fréquence (*support*)
2. **Génération des règles** — à partir des itemsets, dérive des règles `A → B` filtrées par confiance et lift

### Métriques

| Métrique | Formule | Interprétation |
|---|---|---|
| **Support** | `P(A ∩ B)` | Fréquence d'apparition de la paire dans toutes les commandes |
| **Confiance** | `P(B\|A)` | Probabilité que B soit commandé sachant que A l'est |
| **Lift** | `confiance / P(B)` | Ratio vs hasard pur — lift > 1 = corrélation positive réelle |
| **Leverage** | `support(A∩B) − support(A)×support(B)` | Différence absolue vs indépendance |
| **Conviction** | `(1−support(B)) / (1−confiance(A→B))` | Robustesse de la règle, prend en compte la direction |

### Paramètres retenus

```python
min_support    = 0.01   # ≥ ~120 commandes pour qu'une paire soit retenue
min_confidence = 0.05   # seuil bas justifié par 92 produits dans le catalogue
min_lift       = 1.0    # filtre "mieux que le hasard", affinable dans le dashboard
```

> Le support à 1% est calibré sur le volume (12 348 transactions multi-items) et la dispersion du catalogue (92 produits). Tous les seuils sont ajustables en temps réel depuis la sidebar du dashboard.

### Résultats

- **84 itemsets fréquents** extraits
- **70 règles d'association** générées
- **Lift maximum : ~2.98** (*Fried Chicken Peri Peri Tender ↔ Bone in Jamaican Grilled Chicken*)

**Top insight business :** les grillades du restaurant *Swaad* (Bone in Jamaican / Peri Peri / Smoky BBQ / Angara) se commandent très fréquemment ensemble — une stratégie de menu combo "dégustation grillades" serait pertinente.

---

## 🗂️ Structure du projet

```
food-mining-recommender/
│
├── data/
│   └── order_history.csv          # Dataset synthétique (généré, inclus dans le repo)
│
├── mining.py                      # Logique data mining (parsing, Apriori, recommandations)
├── app.py                         # Dashboard Streamlit
├── generate_dataset.py            # Script de génération du dataset synthétique
├── requirements.txt               # Dépendances Python
└── README.md
```

---

## ⚙️ Installation et lancement

### 1. Cloner le repo

```bash
git clone https://github.com/<ton-username>/food-mining-recommender.git
cd food-mining-recommender
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Le dataset est déjà inclus

`data/order_history.csv` est fourni directement dans le repo. Pour le régénérer ou en créer une variante :

```bash
python generate_dataset.py
```

### 4. Lancer le dashboard

```bash
streamlit run app.py
```

Le dashboard s'ouvre sur `http://localhost:8501`

---

## 🌐 Déploiement en ligne (Streamlit Cloud)

Le dashboard est déployable gratuitement sur [Streamlit Community Cloud](https://share.streamlit.io) :

1. Pousser le repo sur GitHub (avec `data/order_history.csv` inclus)
2. Aller sur [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Sélectionner le repo, la branche `main`, et le fichier `app.py`
4. Déployer — l'URL publique est générée automatiquement

---

## 🖥️ Dashboard — Aperçu

Le dashboard Streamlit expose **5 onglets** :

| Onglet | Contenu |
|---|---|
| 📊 Vue d'ensemble | Top 15 plats, répartition par restaurant, distribution des paniers |
| 🔗 Règles d'association | Cartes des règles triées par lift, scatter plot Support/Confiance/Lift |
| 💡 Recommandations | Sélection d'un plat → recommandations en temps réel avec scores |
| 📈 Exploration | Heatmap de co-occurrences, itemsets par taille, distribution du lift |
| 📖 Glossaire & Méthode | Définitions détaillées de chaque métrique avec exemples chiffrés |

**Fonctionnalités interactives :**
- Mode clair / sombre (bouton dans la sidebar)
- 3 sliders ajustables en temps réel (support, confiance, lift)
- Sélecteur de plat pour le moteur de recommandation

---

## 🛠️ Stack technique

| Outil | Rôle |
|---|---|
| `Python 3.11` | Langage principal |
| `pandas` | Manipulation des données |
| `mlxtend` | Algorithme Apriori & règles d'association |
| `plotly` | Visualisations interactives |
| `streamlit` | Dashboard web |
| `re` | Parsing des transactions (regex) |

---

## 📁 Fonctions principales (`mining.py`)

```python
load_transactions(filepath, multi_items_only=True)
# Charge le CSV, parse les items, filtre les commandes 2+ articles

run_apriori(transactions, min_support, min_confidence, min_lift)
# Encode + exécute Apriori → retourne itemsets fréquents + règles triées par lift

get_recommendations(item, rules, top_n=5)
# Retourne les plats les plus associés à un item donné

get_stats(df, transactions)
# KPIs globaux pour le dashboard
```

---

## 💡 Pistes d'amélioration

- [ ] Implémenter **FP-Growth** pour comparer les performances avec Apriori sur grand volume
- [ ] Ajouter un filtre par **restaurant** dans le dashboard
- [ ] Intégrer une **analyse temporelle** (heures de pointe, jours de semaine)
- [ ] Tester sur un dataset e-commerce (ex. Online Retail UCI) pour généraliser l'approche
- [ ] Exporter les règles en JSON/API pour une intégration dans un vrai système de caisse

---

## 👤 Auteur

**Abdoul Rachid Fadé**  
Étudiant MSc Intelligence Artificielle — Epitech  
Data Analyst · Python · SQL · Power BI · Machine Learning

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/ton-profil)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)](https://github.com/ton-username)

---

*Projet réalisé dans le cadre du développement d'un portfolio Data / IA — Juin 2026*
