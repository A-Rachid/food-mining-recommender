"""
generate_dataset.py
-------------------
Génère un dataset synthétique réaliste basé sur la structure du dataset Zomato Delhi NCR.
Fidèle aux vraies proportions : restaurants, plats, fréquences, prix, statuts, zones.
"""

import random
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# 1. CATALOGUE DES RESTAURANTS ET PLATS
# ─────────────────────────────────────────────

RESTAURANTS = {
    "Aura Pizzas": {
        "id": "REST001",
        "subzones": ["Greater Kailash 2 (GK2)", "DLF Phase 1", "Vasant Kunj"],
        "weight": 0.68,  # 68% des commandes
        "menu": {
            # (nom_plat, prix_unitaire, poids_popularité)
            "Pizzas": [
                ("Bageecha Pizza",               349, 0.18),
                ("All About Chicken Pizza",       369, 0.10),
                ("Makhani Paneer Pizza",          319, 0.09),
                ("Margherita Pizza",              279, 0.08),
                ("Tripple Cheese Pizza",          399, 0.06),
                ("Peri Peri Paneer Pizza",        319, 0.05),
                ("Murgh Amritsari Seekh Pizza",   369, 0.05),
                ("Just Pepperoni Pizza",          399, 0.04),
                ("Mushroom Pizza",                299, 0.03),
                ("Peri Peri Grilled Chicken Pizza",369,0.03),
                ("Bellpepper Onion Pizza",        279, 0.02),
                ("Chicken Pepperoni Pizza",       399, 0.02),
                ("Mutton Seekh Pizza",            419, 0.02),
            ],
            "Garlic Breads": [
                ("Chilli Cheese Garlic Bread",   199, 0.11),
                ("Cheesy Garlic Bread",          179, 0.07),
                ("Murgh Amritsari Garlic Bread", 219, 0.04),
                ("Pepperoni Garlic Bread",       229, 0.02),
            ],
            "Melts & Pides": [
                ("Jamaican Chicken Melt",        249, 0.07),
                ("Murgh Amritsari Seekh Melt",   259, 0.03),
                ("Angara Paneer Melt",           239, 0.04),
                ("Mushroom Mozzarella Melt",     239, 0.03),
                ("Peri Peri Chicken Melt",       249, 0.02),
                ("Masala Paneer Pide",           229, 0.04),
                ("Murgh Amritsari Seekh Pide",   249, 0.04),
                ("Spinach Sumac Pide",           219, 0.02),
                ("Mutton Seekh Pide",            279, 0.02),
                ("OG Cheese Pide",               219, 0.02),
                ("Just Pepperoni Pide",          239, 0.02),
            ],
            "Sides": [
                ("Herbed Potato",                99,  0.05),
                ("Peri Peri Crisper Fries",      119, 0.03),
            ],
        }
    },
    "Swaad": {
        "id": "REST002",
        "subzones": ["Sector 4", "Sector 135", "Shahdara"],
        "weight": 0.29,
        "menu": {
            "Grillades": [
                ("Bone in Jamaican Grilled Chicken",   349, 0.22),
                ("Bone in Peri Peri Grilled Chicken",  349, 0.09),
                ("Bone in Smoky Bbq Grilled Chicken",  349, 0.10),
                ("Bone in Kabuli Grilled Chicken",     349, 0.07),
                ("Bone in Angara Grilled Chicken",     349, 0.06),
            ],
            "Tenders": [
                ("Grilled Chicken Jamaican Tender",    199, 0.08),
                ("Fried Chicken Peri Peri Tender",     179, 0.08),
                ("Grilled Chicken Smoky BBQ Tender",   199, 0.05),
                ("Fried Chicken Classic Tender",       159, 0.05),
                ("Fried Chicken Angara Tender",        179, 0.05),
                ("Grilled Chicken Peri Peri Tender",   199, 0.05),
                ("Grilled Chicken Angara Tender",      199, 0.03),
                ("Fried Chicken Ghostbuster Tender",   179, 0.03),
                ("Fried Chicken Kabuli Tender",        179, 0.02),
            ],
            "Burgers": [
                ("AAC Grilled Chicken Burger",         249, 0.03),
                ("Fried Chicken Beast AAC Burger",     269, 0.02),
            ],
            "Sides & Extras": [
                ("Animal Fries",                       129, 0.10),
                ("Salted Fries",                        89, 0.02),
                ("AAC Signature Fries",                129, 0.01),
                ("AAC Saucy Fries",                    129, 0.01),
                ("Peri Peri Crisper Fries",            119, 0.01),
                ("Peri Peri Fries",                    109, 0.01),
                ("Herbed Potato",                       99, 0.01),
                ("Garlic Aioli",                        49, 0.01),
                ("Angara Rice",                         89, 0.01),
            ],
        }
    },
    "Dilli Burger Adda": {
        "id": "REST003",
        "subzones": ["Greater Kailash 2 (GK2)", "DLF Phase 1"],
        "weight": 0.015,
        "menu": {
            "Burgers": [
                ("Mutton Smashed Burger",              299, 0.22),
                ("Grilled Chicken Dirty Burger",       269, 0.16),
                ("Classic Bacon Melt Tenderloin Burger",349,0.06),
                ("Atomic Veg Burger",                  219, 0.06),
                ("Tenderloin Smashed Burger",          329, 0.05),
                ("Grilled Paneer Burger",              239, 0.05),
                ("Chicken Smashed Burger",             279, 0.05),
                ("Cheesy Veg Burger",                  199, 0.04),
                ("Korean Fried Chicken Burger",        279, 0.04),
                ("Fried Mushroom Burger",              239, 0.03),
            ],
            "Fries": [
                ("Dirty Saucy Fries",                  149, 0.21),
                ("Peri Peri Fries",                    109, 0.06),
                ("Peri Peri Crisper Fries",            119, 0.04),
                ("Dirty Indian Masala Fries",          149, 0.04),
                ("Dirty Saucy Chicken Loaded Fries",   189, 0.04),
                ("Salted Fries",                        89, 0.04),
                ("Onion Rings",                        129, 0.04),
            ],
        }
    },
    "Tandoori Junction": {
        "id": "REST004",
        "subzones": ["Sector 135", "Greater Kailash 2 (GK2)"],
        "weight": 0.010,
        "menu": {
            "Grillades": [
                ("Chicken 65 Boneless Grilled Chicken Breast",   349, 0.22),
                ("Angara Boneless Grilled Chicken Breast",       349, 0.21),
                ("Smoky BBQ Boneless Grilled Chicken Breast",    349, 0.14),
                ("Peri Peri Boneless Grilled Chicken Breast",    349, 0.14),
                ("Carribean Jerk Boneless Grilled Chicken Breast",349,0.11),
                ("Malvani Boneless Grilled Chicken Breast",      349, 0.05),
                ("Carribean Jerk Grilled Chicken Quarter",       299, 0.07),
            ],
            "Sides": [
                ("Grlld Masala Fries",   129, 0.05),
                ("Peri Peri Fries",      109, 0.05),
                ("Grlld Vegetables",     119, 0.05),
                ("Salted Fries",          89, 0.03),
                ("Coleslaw",              79, 0.04),
                ("Angara Rice",           89, 0.02),
            ],
        }
    },
    "The Chicken Junction": {
        "id": "REST005",
        "subzones": ["Vasant Kunj", "DLF Phase 1"],
        "weight": 0.003,
        "menu": {
            "Poulet": [
                ("Fried Chicken Tangdi - 2pcs",          199, 0.27),
                ("Fried Chicken Boneless Bites - 6pcs",  179, 0.25),
                ("Fried Chicken Bites (Bone) - 4pcs",    149, 0.10),
                ("Fried Chicken Boneless Bites - 10pcs", 269, 0.04),
            ],
            "Frites & Sauces": [
                ("Desi Masala Fries",          129, 0.17),
                ("Salted Fries",                89, 0.13),
                ("Peri Peri Fries",            109, 0.10),
                ("Dynamite sauce",              49, 0.17),
                ("Mint Mayonnaise",             49, 0.06),
                ("Garlic Aioli",                49, 0.04),
            ],
        }
    },
    "Masala Junction": {
        "id": "REST006",
        "subzones": ["Shahdara", "Sector 4"],
        "weight": 0.002,
        "menu": {
            "Sliders": [
                ("Fried Paneer Angara Slider",      149, 0.15),
                ("Grilled Paneer Angara Slider",    149, 0.12),
                ("Korean Fried Chicken Slider",     159, 0.08),
                ("Fried Chicken Angara Slider",     149, 0.04),
                ("Grilled Paneer Afghani Slider",   149, 0.04),
                ("Grilled Chicken Jamaican Slider", 159, 0.04),
            ],
            "Frites": [
                ("Ooh Saucy Fries",        139, 0.40),
                ("Peri Peri Fries",        109, 0.12),
                ("Salted Fries",            89, 0.08),
                ("Ooh Masala Fries",       139, 0.04),
            ],
        }
    },
}

# ─────────────────────────────────────────────
# 2. FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────

def get_flat_menu(resto_data):
    """Retourne liste plate [(nom, prix, poids)] depuis le menu par catégorie."""
    items, weights = [], []
    for cat_items in resto_data["menu"].values():
        for name, price, w in cat_items:
            items.append((name, price))
            weights.append(w)
    total = sum(weights)
    weights = [w / total for w in weights]
    return items, weights

def generate_basket(items, weights):
    """Génère un panier réaliste : distribution ~70% 1-item, 25% 2-items, etc."""
    r = random.random()
    if r < 0.44:
        n = 1
    elif r < 0.83:
        n = 2
    elif r < 0.94:
        n = 3
    elif r < 0.98:
        n = 4
    else:
        n = random.randint(5, 7)

    chosen = random.choices(items, weights=weights, k=n * 3)
    # Dédupliquer tout en respectant l'ordre
    seen, unique = set(), []
    for item in chosen:
        if item[0] not in seen:
            seen.add(item[0])
            unique.append(item)
        if len(unique) == n:
            break
    if not unique:
        unique = [random.choices(items, weights=weights)[0]]
    return unique

def format_items(basket):
    """Format : '1 x Pizza, 2 x Frites'"""
    counts = {}
    for name, price in basket:
        counts[name] = counts.get(name, 0) + 1
    return ", ".join(f"{qty} x {name}" for name, qty in counts.items())

def generate_datetime(start, end):
    """Date aléatoire entre start et end, heures de pointe réalistes."""
    delta = (end - start).total_seconds()
    rand_sec = random.random() * delta
    dt = start + timedelta(seconds=rand_sec)
    # Heures de pointe : midi, soir, nuit
    hour_weights = [
        3,3,3,2,0,0,0,0,0,0,0,2,   # 0-11
        5,6,5,4,4,5,6,7,6,5,4,3    # 12-23
    ]
    hour = random.choices(range(24), weights=hour_weights)[0]
    minute = random.randint(0, 59)
    return dt.replace(hour=hour, minute=minute)

def fake_customer_id():
    return hashlib.sha1(str(random.random()).encode()).hexdigest()

def compute_total(subtotal, status):
    """Applique remise aléatoire selon statut."""
    if status != "Delivered":
        return subtotal, 0, 0, 0
    packaging = round(subtotal * random.uniform(0.03, 0.06), 2)
    promo_pct = random.choices([0, 0.10, 0.15, 0.20, 0.40], weights=[40,20,15,15,10])[0]
    promo_cap = random.choice([80, 100, 120, 150, 175])
    promo = min(subtotal * promo_pct, promo_cap) if promo_pct > 0 else 0
    total = round(subtotal + packaging - promo, 2)
    return total, packaging, promo, 0

# ─────────────────────────────────────────────
# 3. GÉNÉRATION
# ─────────────────────────────────────────────

N_ORDERS = 22000
START    = datetime(2024, 9, 1)
END      = datetime(2025, 1, 31)

RESTO_NAMES   = list(RESTAURANTS.keys())
RESTO_WEIGHTS = [RESTAURANTS[r]["weight"] for r in RESTO_NAMES]

STATUS_WEIGHTS = [0.991, 0.007, 0.001, 0.001]
STATUSES       = ["Delivered", "Rejected", "Returned", "Timed out"]

DISTANCES = ["<1km", "1km", "2km", "3km", "4km", "5km", "6km"]
DIST_W    = [0.10, 0.20, 0.25, 0.20, 0.12, 0.08, 0.05]

rows = []
order_id_base = 6100000000

for i in range(N_ORDERS):
    # Restaurant
    resto_name  = random.choices(RESTO_NAMES, weights=RESTO_WEIGHTS)[0]
    resto_data  = RESTAURANTS[resto_name]
    subzone     = random.choice(resto_data["subzones"])

    # Panier
    items, weights = get_flat_menu(resto_data)
    basket = generate_basket(items, weights)
    items_str = format_items(basket)

    # Prix
    subtotal = sum(price for name, price in basket) + random.randint(-30, 50)
    subtotal = max(50, round(subtotal / 5) * 5)

    # Statut
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

    # Financier
    total, packaging, promo, gold = compute_total(subtotal, status)

    # Date
    order_dt = generate_datetime(START, END)
    order_dt_str = order_dt.strftime("%I:%M %p, %B %d %Y")

    # Rating (seulement si livré)
    rating = None
    if status == "Delivered" and random.random() < 0.35:
        rating = random.choices([1,2,3,4,5], weights=[1,2,5,25,67])[0]

    # KPT & Rider
    kpt  = round(random.gauss(18, 4), 1) if status == "Delivered" else None
    wait = round(random.gauss(8, 4), 1)  if status == "Delivered" else None
    if wait: wait = max(0, wait)

    rows.append({
        "Restaurant ID":                                  resto_data["id"],
        "Restaurant name":                                resto_name,
        "Subzone":                                        subzone,
        "City":                                           "Delhi NCR",
        "Order ID":                                       order_id_base + i,
        "Order Placed At":                                order_dt_str,
        "Order Status":                                   status,
        "Delivery":                                       "Zomato Delivery",
        "Distance":                                       random.choices(DISTANCES, weights=DIST_W)[0],
        "Items in order":                                 items_str,
        "Bill subtotal":                                  float(subtotal),
        "Packaging charges":                              packaging if status == "Delivered" else None,
        "Restaurant discount (Promo)":                    promo if status == "Delivered" else None,
        "Total":                                          total if status == "Delivered" else None,
        "Rating":                                         float(rating) if rating else None,
        "KPT duration (minutes)":                         kpt,
        "Rider wait time (minutes)":                      wait,
        "Customer ID":                                    fake_customer_id(),
    })

df_synth = pd.DataFrame(rows)
df_synth = df_synth.sort_values("Order Placed At").reset_index(drop=True)

# ─────────────────────────────────────────────
# 4. EXPORT
# ─────────────────────────────────────────────

df_synth.to_csv("data/order_history.csv", index=False)


print("✅ Dataset généré !")
print(f"   {len(df_synth):,} commandes")
print(f"   {df_synth['Restaurant name'].nunique()} restaurants")
print(f"   Période : {df_synth['Order Placed At'].iloc[0]} → {df_synth['Order Placed At'].iloc[-1]}")
print(f"   Status : {dict(df_synth['Order Status'].value_counts())}")
print(f"   Rating moyen (livrées) : {df_synth['Rating'].mean():.2f}")
print()

# Vérif panier
import re
def parse_items(raw):
    if pd.isna(raw): return []
    return [i.strip() for i in re.findall(r'\d+ x (.+?)(?:,|$)', str(raw))]

df_synth['items_list'] = df_synth['Items in order'].apply(parse_items)
df_synth['nb_items']   = df_synth['items_list'].apply(len)
from collections import Counter
all_items = [i for sub in df_synth['items_list'] for i in sub]

print(f"   Produits uniques : {len(set(all_items))}")
print(f"   Distribution paniers :\n{df_synth['nb_items'].value_counts().sort_index().to_string()}")
print()
print("   Top 10 plats :")
for item, cnt in Counter(all_items).most_common(10):
    print(f"     {cnt:5d}x  {item}")
