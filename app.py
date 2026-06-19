"""
app.py — Food Mining Dashboard v2
Mode clair / sombre · Cartes avec bordures · Onglet glossaire KPIs
"""

import re
import warnings
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from mining import load_transactions, run_apriori, get_recommendations, get_stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Food Mining — Recommandation de plats",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THÈME CLAIR / SOMBRE
# ─────────────────────────────────────────────

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Palettes
DARK = {
    "bg":           "#0f1117",
    "bg2":          "#161b27",
    "card":         "#1a2035",
    "card_border":  "#2a3555",
    "sidebar":      "#161b27",
    "text":         "#e2e8f0",
    "text2":        "#94a3b8",
    "text3":        "#64748b",
    "accent":       "#f97316",
    "accent2":      "#3b82f6",
    "rule_border":  "#f97316",
    "grid":         "#1e2640",
    "plot_bg":      "rgba(0,0,0,0)",
    "paper_bg":     "rgba(0,0,0,0)",
    "kpi_grad1":    "#1a2035",
    "kpi_grad2":    "#1e2640",
}

LIGHT = {
    "bg":           "#f5f6fa",
    "bg2":          "#ffffff",
    "card":         "#ffffff",
    "card_border":  "#e2e6f0",
    "sidebar":      "#ffffff",
    "text":         "#1e293b",
    "text2":        "#475569",
    "text3":        "#94a3b8",
    "accent":       "#e85d04",
    "accent2":      "#2563eb",
    "rule_border":  "#e85d04",
    "grid":         "#f1f5f9",
    "plot_bg":      "rgba(0,0,0,0)",
    "paper_bg":     "rgba(0,0,0,0)",
    "kpi_grad1":    "#ffffff",
    "kpi_grad2":    "#f8fafc",
}

T = DARK if st.session_state.dark_mode else LIGHT

# ─────────────────────────────────────────────
# CSS DYNAMIQUE
# ─────────────────────────────────────────────

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background-color: {T['bg']};
    }}

    [data-testid="stSidebar"] {{
        background-color: {T['sidebar']};
        border-right: 1px solid {T['card_border']};
    }}
    [data-testid="stSidebar"] * {{
        color: {T['text']} !important;
    }}

    /* Sliders */
    [data-testid="stSlider"] label {{ color: {T['text2']} !important; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {T['card']};
        border-radius: 10px;
        padding: 4px;
        border: 1px solid {T['card_border']};
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        color: {T['text2']} !important;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {T['accent']} !important;
        color: #fff !important;
    }}

    /* KPI cards */
    .kpi-card {{
        background: linear-gradient(135deg, {T['kpi_grad1']} 0%, {T['kpi_grad2']} 100%);
        border: 1.5px solid {T['card_border']};
        border-radius: 14px;
        padding: 22px 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.15s;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.10); }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {T['accent']};
        line-height: 1.1;
    }}
    .kpi-label {{
        font-size: 0.72rem;
        color: {T['text2']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 5px;
        font-weight: 600;
    }}

    /* Section title */
    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {T['text']};
        border-left: 4px solid {T['accent']};
        padding-left: 10px;
        margin-bottom: 14px;
        display: block;
    }}

    /* Chart card wrapper */
    .chart-card {{
        background: {T['card']};
        border: 1.5px solid {T['card_border']};
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }}

    /* Rule cards */
    .rule-card {{
        background: {T['card']};
        border: 1.5px solid {T['card_border']};
        border-left: 5px solid {T['rule_border']};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        transition: box-shadow 0.15s;
    }}
    .rule-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.10); }}
    .rule-ant  {{ font-size: 0.95rem; color: {T['text']}; font-weight: 600; }}
    .rule-cons {{ font-size: 0.9rem; color: {T['accent']}; margin-top: 2px; }}
    .rule-meta {{ font-size: 0.73rem; color: {T['text3']}; margin-top: 6px; }}
    .lift-high   {{ color: #16a34a; font-weight: 700; }}
    .lift-medium {{ color: {T['accent']}; font-weight: 700; }}
    .lift-low    {{ color: {T['text3']}; font-weight: 600; }}

    /* Reco cards */
    .reco-card {{
        background: {T['card']};
        border: 1.5px solid {T['card_border']};
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}
    .reco-name  {{ color: {T['text']}; font-weight: 600; font-size: 0.95rem; }}
    .reco-score {{ font-size: 0.76rem; color: {T['text2']}; margin-top: 3px; }}

    /* Glossaire cards */
    .gloss-card {{
        background: {T['card']};
        border: 1.5px solid {T['card_border']};
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .gloss-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {T['accent']};
        margin-bottom: 6px;
    }}
    .gloss-formula {{
        font-family: monospace;
        font-size: 0.85rem;
        background: {T['bg']};
        border: 1px solid {T['card_border']};
        border-radius: 6px;
        padding: 6px 10px;
        color: {T['accent2']};
        margin: 8px 0;
        display: inline-block;
    }}
    .gloss-body {{ font-size: 0.88rem; color: {T['text2']}; line-height: 1.6; }}
    .gloss-example {{
        font-size: 0.82rem;
        background: {T['bg']};
        border-left: 3px solid {T['accent']};
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        color: {T['text2']};
        margin-top: 8px;
    }}
    .interp-row {{
        display: flex;
        gap: 8px;
        margin-top: 8px;
        flex-wrap: wrap;
    }}
    .interp-badge {{
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid {T['card_border']};
        color: {T['text2']};
        background: {T['bg']};
    }}

    h1, h2, h3 {{ color: {T['text']} !important; }}
    p {{ color: {T['text2']}; }}
    .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
    div[data-testid="stMetric"] label {{ color: {T['text2']} !important; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────

@st.cache_data
def load_data(path, min_support, min_confidence, min_lift):
    df, transactions = load_transactions(path, multi_items_only=True)
    frequent_itemsets, rules = run_apriori(
        transactions, min_support=min_support,
        min_confidence=min_confidence, min_lift=min_lift,
    )
    stats = get_stats(df, transactions)
    return df, transactions, frequent_itemsets, rules, stats

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    # Toggle thème
    col_logo, col_toggle = st.columns([2, 1])
    with col_logo:
        st.markdown(f"## 🍽️ Food Mining")
        st.markdown(f"<span style='color:{T['text2']};font-size:0.8rem'>Analyse de paniers restaurant</span>", unsafe_allow_html=True)
    with col_toggle:
        st.markdown("<br>", unsafe_allow_html=True)
        mode_label = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(mode_label, help="Basculer mode sombre / clair"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.divider()
    st.markdown(f"### ⚙️ Paramètres Apriori")

    min_support = st.slider("Support minimum", 0.005, 0.10, 0.01, 0.005, format="%.3f",
        help="Fréquence minimale d'une paire dans toutes les commandes.")
    min_confidence = st.slider("Confiance minimum", 0.01, 0.50, 0.05, 0.01, format="%.2f",
        help="Probabilité que B soit commandé sachant que A l'est.")
    min_lift = st.slider("Lift minimum", 1.0, 6.0, 1.0, 0.1, format="%.1f",
        help="Lift > 1 = meilleur que le hasard.")

    st.divider()
    st.markdown("### 🔍 Recommandation")

    DATA_PATH = "data/order_history.csv"

with st.spinner("Analyse en cours..."):
    df, transactions, frequent_itemsets, rules, stats = load_data(
        DATA_PATH, min_support, min_confidence, min_lift
    )

all_items_flat = sorted(set(item for basket in transactions for item in basket))

with st.sidebar:
    selected_item = st.selectbox("Plat sélectionné",
        options=["— choisir un plat —"] + all_items_flat, index=0)
    top_n = st.slider("Nb de recommandations", 1, 10, 5)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown(f"""
<h1 style='margin-bottom:2px;color:{T['text']}'>🍽️ Food Mining — Recommandation de plats</h1>
<p style='color:{T['text3']};margin-bottom:24px;font-size:0.9rem'>
    Analyse des règles d'association · Dataset Zomato Delhi NCR · 2024–2025
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, f"{stats['nb_commandes_total']:,}", "Commandes totales"),
    (k2, f"{stats['nb_commandes_multi']:,}", "Commandes multi-items"),
    (k3, str(stats['nb_items_uniques']),     "Produits uniques"),
    (k4, str(len(rules)),                    "Règles générées"),
    (k5, f"{rules['lift'].max():.2f}" if not rules.empty else "—", "Lift maximum"),
]
for col, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Couleurs graphiques selon thème
ACCENT      = T['accent']
ACCENT2     = T['accent2']
COLOR_SEQ   = [T['accent2'], T['accent'], "#16a34a", "#a855f7", "#ec4899", "#14b8a6"]
GRID_COL    = T['grid']
FONT_COL    = T['text2']
PAPER_BG    = T['paper_bg']
PLOT_BG     = T['plot_bg']

def chart_layout(fig, height=360):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font_color=FONT_COL, margin=dict(l=4, r=4, t=10, b=10),
        height=height, legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
    )
    fig.update_xaxes(gridcolor=GRID_COL, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COL, zeroline=False)
    return fig

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Vue d'ensemble",
    "🔗 Règles d'association",
    "💡 Recommandations",
    "📈 Exploration",
    "📖 Glossaire & Méthode",
])

# ══════════════════════════════════════════════
# TAB 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════

with tab1:
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown(f'<span class="section-title">Top 15 plats les plus commandés</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        top_items = stats["top_items"].head(15)
        fig_top = px.bar(
            x=top_items.values, y=top_items.index, orientation="h",
            color=top_items.values,
            color_continuous_scale=[[0, ACCENT2], [1, ACCENT]],
            labels={"x": "Nb commandes", "y": ""},
        )
        fig_top.update_traces(marker_line_width=0)
        fig_top.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, coloraxis_showscale=False)
        chart_layout(fig_top, 400)
        st.plotly_chart(fig_top, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown(f'<span class="section-title">Répartition par restaurant</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        resto_counts = stats["restaurants"]
        fig_pie = px.pie(
            values=resto_counts.values, names=resto_counts.index,
            hole=0.52, color_discrete_sequence=COLOR_SEQ,
        )
        fig_pie.update_traces(textfont_size=11, pull=[0.03]*len(resto_counts))
        chart_layout(fig_pie, 220)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<span class="section-title">Articles par commande</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        nb_dist = df["nb_items"].value_counts().sort_index()
        fig_dist = px.bar(
            x=nb_dist.index, y=nb_dist.values,
            color=nb_dist.values,
            color_continuous_scale=[[0, ACCENT2], [1, ACCENT]],
            labels={"x": "Nb articles", "y": "Commandes"},
            text=nb_dist.values,
        )
        fig_dist.update_traces(textposition="outside", marker_line_width=0)
        fig_dist.update_layout(showlegend=False, coloraxis_showscale=False)
        chart_layout(fig_dist, 190)
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — RÈGLES D'ASSOCIATION
# ══════════════════════════════════════════════

with tab2:
    if rules.empty:
        st.warning("Aucune règle trouvée. Essaie de baisser le support ou le lift dans la sidebar.")
    else:
        col_rules, col_scatter = st.columns([1, 1.2])

        with col_rules:
            st.markdown(f'<span class="section-title">Top règles par lift ({len(rules)} générées)</span>', unsafe_allow_html=True)
            for _, row in rules.head(12).iterrows():
                lv = row["lift"]
                lc = "lift-high" if lv >= 3 else ("lift-medium" if lv >= 1.5 else "lift-low")
                st.markdown(f"""
                <div class="rule-card">
                    <div class="rule-ant">🛒 {row['antecedents']}</div>
                    <div class="rule-cons">→ {row['consequents']}</div>
                    <div class="rule-meta">
                        support <b>{row['support']:.3f}</b> &nbsp;|&nbsp;
                        confiance <b>{row['confidence']:.1%}</b> &nbsp;|&nbsp;
                        lift <span class="{lc}">{lv:.2f}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_scatter:
            st.markdown(f'<span class="section-title">Support vs Confiance · taille = lift</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            fig_sc = px.scatter(
                rules, x="support", y="confidence", size="lift", color="lift",
                hover_data={"antecedents": True, "consequents": True, "lift": ":.2f"},
                color_continuous_scale=[[0, ACCENT2], [0.5, ACCENT], [1, "#16a34a"]],
                size_max=32,
                labels={"support": "Support", "confidence": "Confiance", "lift": "Lift"},
            )
            chart_layout(fig_sc, 430)
            st.plotly_chart(fig_sc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<span class="section-title">Tableau complet des règles</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        disp = rules.copy()
        disp["support"]    = disp["support"].map("{:.4f}".format)
        disp["confidence"] = disp["confidence"].map("{:.2%}".format)
        disp["lift"]       = disp["lift"].map("{:.2f}".format)
        disp["leverage"]   = disp["leverage"].map("{:.4f}".format)
        disp["conviction"] = disp["conviction"].map("{:.2f}".format)
        st.dataframe(disp, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — RECOMMANDATIONS
# ══════════════════════════════════════════════

with tab3:
    if selected_item == "— choisir un plat —":
        st.info("👈 Sélectionne un plat dans la sidebar pour démarrer le moteur de recommandation.")
    else:
        reco = get_recommendations(selected_item, rules, top_n=top_n)
        col_reco, col_chart = st.columns([1, 1])

        with col_reco:
            st.markdown(f'<span class="section-title">Recommandations pour · {selected_item}</span>', unsafe_allow_html=True)
            st.markdown(f"<span style='color:{T['text2']};font-size:0.85rem'>{len(reco)} association(s) trouvée(s)</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if reco.empty:
                st.warning("Pas d'association trouvée. Essaie de baisser le lift minimum dans la sidebar.")
            else:
                for _, row in reco.iterrows():
                    icon = "🔥" if row["lift"] >= 3 else ("⭐" if row["lift"] >= 1.5 else "✓")
                    st.markdown(f"""
                    <div class="reco-card">
                        <div>
                            <div class="reco-name">🍴 {row['produit_recommandé']}</div>
                            <div class="reco-score">
                                Confiance {row['confiance']:.1%} &nbsp;·&nbsp; Lift {row['lift']:.2f}
                            </div>
                        </div>
                        <div style="font-size:1.5rem">{icon}</div>
                    </div>""", unsafe_allow_html=True)

        with col_chart:
            if not reco.empty:
                st.markdown(f'<span class="section-title">Scores de recommandation</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
                fig_reco = px.bar(
                    reco, x="lift", y="produit_recommandé", orientation="h",
                    color="confiance",
                    color_continuous_scale=[[0, ACCENT2], [1, ACCENT]],
                    labels={"lift": "Lift", "produit_recommandé": "", "confiance": "Confiance"},
                    text="lift",
                )
                fig_reco.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_width=0)
                fig_reco.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
                chart_layout(fig_reco, 280)
                st.plotly_chart(fig_reco, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="chart-card">
                <span class="section-title">Lecture des scores</span>
                <table style="width:100%;font-size:0.85rem;border-collapse:collapse">
                    <tr style="color:{T['text3']};font-size:0.72rem;text-transform:uppercase">
                        <th style="text-align:left;padding:6px 0">Symbole</th>
                        <th style="text-align:left;padding:6px 0">Lift</th>
                        <th style="text-align:left;padding:6px 0">Interprétation</th>
                    </tr>
                    <tr style="color:{T['text']}"><td>🔥</td><td>≥ 3.0</td><td>Association très forte</td></tr>
                    <tr style="color:{T['text']}"><td>⭐</td><td>1.5 – 3.0</td><td>Association significative</td></tr>
                    <tr style="color:{T['text']}"><td>✓</td><td>1.0 – 1.5</td><td>Légèrement corrélé</td></tr>
                </table>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — EXPLORATION
# ══════════════════════════════════════════════

with tab4:
    col_heat, col_freq = st.columns([1.3, 1])

    with col_heat:
        st.markdown(f'<span class="section-title">Heatmap des co-occurrences · Top 15 plats</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        top15 = stats["top_items"].head(15).index.tolist()
        matrix = pd.DataFrame(0, index=top15, columns=top15)
        for basket in transactions:
            bt = [i for i in basket if i in top15]
            for i in range(len(bt)):
                for j in range(len(bt)):
                    if i != j:
                        matrix.loc[bt[i], bt[j]] += 1
        matrix_norm = matrix.div(matrix.max().max())
        short = [n[:16] + "…" if len(n) > 16 else n for n in top15]
        fig_heat = go.Figure(data=go.Heatmap(
            z=matrix_norm.values, x=short, y=short,
            colorscale=[[0, T['bg']], [0.5, ACCENT2], [1, ACCENT]],
            showscale=True,
            hovertemplate="<b>%{y}</b> + <b>%{x}</b><br>Co-occurrences : %{text}<extra></extra>",
            text=matrix.values,
        ))
        fig_heat.update_layout(xaxis=dict(tickangle=-40, tickfont_size=10), yaxis=dict(tickfont_size=10))
        chart_layout(fig_heat, 430)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_freq:
        st.markdown(f'<span class="section-title">Itemsets fréquents par taille</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        freq_by_len = frequent_itemsets.groupby("length").size().reset_index(name="count")
        freq_by_len["label"] = freq_by_len["length"].astype(str) + " item(s)"
        fig_freq = px.bar(
            freq_by_len, x="label", y="count",
            color="count", color_continuous_scale=[[0, ACCENT2], [1, ACCENT]],
            text="count", labels={"label": "Taille", "count": "Nb d'itemsets"},
        )
        fig_freq.update_traces(textposition="outside", marker_line_width=0)
        fig_freq.update_layout(coloraxis_showscale=False)
        chart_layout(fig_freq, 250)
        st.plotly_chart(fig_freq, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if not rules.empty:
            st.markdown(f'<span class="section-title">Distribution du lift</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            fig_lh = px.histogram(
                rules, x="lift", nbins=15,
                color_discrete_sequence=[ACCENT],
                labels={"lift": "Lift", "count": "Nb de règles"},
            )
            fig_lh.update_layout(bargap=0.05)
            chart_layout(fig_lh, 200)
            st.plotly_chart(fig_lh, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — GLOSSAIRE & MÉTHODE
# ══════════════════════════════════════════════

with tab5:
    st.markdown(f'<h3 style="color:{T["text"]}">📖 Glossaire des métriques & Méthode</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{T["text2"]};margin-bottom:24px">Toutes les métriques calculées par l\'algorithme Apriori, expliquées simplement avec des exemples tirés du dataset.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # SUPPORT
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">📊 Support</div>
            <div class="gloss-body">Mesure la <b>fréquence</b> d'une association dans l'ensemble des commandes. C'est le filtre de base : en dessous du seuil, la règle est ignorée car trop rare pour être significative.</div>
            <div class="gloss-formula">support(A → B) = nb commandes(A ∩ B) / nb total commandes</div>
            <div class="gloss-example">
                <b>Exemple :</b> Bageecha Pizza + Chilli Cheese Garlic Bread apparaissent ensemble dans 479 commandes sur 11 694.<br>
                → support = 479 / 11 694 = <b>0.041</b>
            </div>
            <div class="interp-row">
                <span class="interp-badge">≥ 0.05 → très fréquent</span>
                <span class="interp-badge">0.01–0.05 → fréquent</span>
                <span class="interp-badge">< 0.01 → rare</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CONFIANCE
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">🎯 Confiance (Confidence)</div>
            <div class="gloss-body">Mesure la <b>probabilité conditionnelle</b> : parmi tous les clients qui commandent A, quelle proportion commande aussi B ? C'est la force prédictive de la règle.</div>
            <div class="gloss-formula">confidence(A → B) = support(A ∩ B) / support(A)</div>
            <div class="gloss-example">
                <b>Exemple :</b> Murgh Amritsari Seekh Melt → Jamaican Chicken Melt<br>
                → confiance = <b>41.6%</b> : sur 10 clients qui prennent le Murgh, ~4 prennent aussi le Jamaican.
            </div>
            <div class="interp-row">
                <span class="interp-badge">≥ 30% → très fiable</span>
                <span class="interp-badge">10–30% → fiable</span>
                <span class="interp-badge">< 10% → incertain</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # LIFT
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">🚀 Lift</div>
            <div class="gloss-body">Mesure si l'association est <b>meilleure que le hasard</b>. Il compare la confiance observée à la probabilité qu'on obtiendrait si A et B étaient totalement indépendants. C'est la métrique la plus importante pour évaluer la qualité d'une règle.</div>
            <div class="gloss-formula">lift(A → B) = confidence(A → B) / support(B)</div>
            <div class="gloss-example">
                <b>Exemple :</b> Jamaican Chicken Melt est commandé dans 7% des paniers (support = 0.07).<br>
                Avec le Murgh, la confiance monte à 41.6%.<br>
                → lift = 0.416 / 0.07 = <b>5.88</b> : l'association est 5.88× plus forte que le hasard.
            </div>
            <div class="interp-row">
                <span class="interp-badge" style="color:#16a34a;border-color:#16a34a">🔥 ≥ 3 → très forte</span>
                <span class="interp-badge" style="color:{T['accent']};border-color:{T['accent']}">⭐ 1.5–3 → significative</span>
                <span class="interp-badge">= 1 → hasard pur</span>
                <span class="interp-badge">< 1 → répulsion</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # LEVERAGE
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">⚖️ Leverage</div>
            <div class="gloss-body">Mesure la <b>différence absolue</b> entre la fréquence observée de la paire et ce qu'on attendrait si A et B étaient indépendants. Contrairement au lift (ratio), le leverage est une différence — il est plus sensible aux items rares.</div>
            <div class="gloss-formula">leverage(A → B) = support(A ∩ B) − support(A) × support(B)</div>
            <div class="gloss-example">
                <b>Exemple :</b> Si Bageecha Pizza (support 0.267) et Chilli Cheese Garlic Bread (support 0.150) étaient indépendants, on attendrait : 0.267 × 0.150 = 0.040.<br>
                On observe support = 0.041 → leverage = 0.041 − 0.040 = <b>+0.001</b><br>
                Positif = ils s'attirent légèrement.
            </div>
            <div class="interp-row">
                <span class="interp-badge">= 0 → indépendants</span>
                <span class="interp-badge">> 0 → corrélation positive</span>
                <span class="interp-badge">< 0 → corrélation négative</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CONVICTION
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">🔒 Conviction</div>
            <div class="gloss-body">Mesure à quel point la règle serait <b>incorrecte si A et B étaient indépendants</b>. Elle intègre la direction de la règle (A → B ≠ B → A) et pénalise les règles qui échoueraient souvent. Une conviction élevée signifie que la règle est robuste.</div>
            <div class="gloss-formula">conviction(A → B) = (1 − support(B)) / (1 − confidence(A → B))</div>
            <div class="gloss-example">
                <b>Exemple :</b> Murgh → Jamaican : conviction = (1 − 0.07) / (1 − 0.416) = 0.93 / 0.584 = <b>1.59</b><br>
                → La règle est 1.59× plus fiable que si les deux plats étaient indépendants.
            </div>
            <div class="interp-row">
                <span class="interp-badge">= 1 → règle aléatoire</span>
                <span class="interp-badge">> 1 → règle fiable</span>
                <span class="interp-badge">→ ∞ → règle parfaite (confiance = 100%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ALGORITHME
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">⚙️ L'algorithme Apriori — en bref</div>
            <div class="gloss-body">
                L'Apriori repose sur une propriété mathématique simple : <b>si une paire est rare, tout itemset qui la contient est aussi rare</b>. Il procède en deux étapes :<br><br>
                <b>1. Génération des itemsets fréquents</b> — part des items seuls, garde ceux au-dessus du support minimum, puis construit des paires, des triplets… en élagage à chaque niveau.<br><br>
                <b>2. Dérivation des règles</b> — pour chaque itemset fréquent, génère toutes les règles possibles et filtre par confiance et lift.<br><br>
                <b>Complexité :</b> exponentielle dans le pire cas, mais l'élagage rend l'algorithme pratique sur des datasets réels.
            </div>
            <div class="gloss-example">
                <b>Sur ce dataset :</b> 226 produits → 74 itemsets fréquents (seuil 1%) → 30 règles d'association finales.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.divider()
st.markdown(f"""
<p style='text-align:center;color:{T["text3"]};font-size:0.78rem'>
    Food Mining · Apriori Association Rules · Dataset Zomato Delhi NCR (2024–2025) · Built with Streamlit & mlxtend
</p>
""", unsafe_allow_html=True)
