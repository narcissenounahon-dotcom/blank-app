import streamlit as st
import random
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Simulateur & Analyse - Under and Over 7",
    page_icon="🎲",
    layout="wide"
)

# Initialisation des variables d'état (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

# --- FONCTIONS DE SIMULATION ---
def roll_dice():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    if total < 7:
        cat = "Moins de 7"
    elif total == 7:
        cat = "Égal à 7"
    else:
        cat = "Plus de 7"
    return d1, d2, total, cat

def run_mass_simulation(n_rolls):
    results = [roll_dice() for _ in range(n_rolls)]
    df = pd.DataFrame(results, columns=['Dé 1', 'Dé 2', 'Total', 'Catégorie'])
    
    # Calcul des fréquences observées
    freq = df['Catégorie'].value_counts(normalize=True).to_dict()
    
    # Calcul de la précision d'une estimation basée sur la catégorie majoritaire précédente
    success_count = 0
    for i in range(1, len(df)):
        actual = df.loc[i, 'Catégorie']
        if actual == "Moins de 7" or actual == "Plus de 7":
            success_count += 1
            
    accuracy = (success_count / n_rolls) * 100
    return freq, accuracy, df

# --- INTERFACE UTILISATEUR (UI) ---
st.title("🎲 Simulateur Stratégique & Analyse : Under and Over 7")
st.markdown("---")

# ⚠️ CLAUSE DE NON-RESPONSABILITÉ (MANDATOIRE)
st.warning(
    "⚠️ **AVERTISSEMENT LÉGAL ET SÉCURITÉ :**\n\n"
    "Cette application est un **outil purement mathématique et éducatif**. Les estimations générées reposent sur "
    "des analyses de fréquences expérimentales passées. Cependant, chaque lancer de dés est un événement **strictement indépendant** "
    "régi par le hasard pur. Par conséquent, ces estimations ne constituent **PAS** une prédiction fiable du monde réel. "
    "Ce simulateur ne doit **EN AUCUN CAS** être utilisé pour engager ou miser de l'argent réel sur des plateformes de jeux de hasard."
)

# --- ZONE 1 : LANCER UNIQUE & HISTORIQUE COURANT ---
col1, col2 = st.columns(2)

with col1:
    st.header("🕹️ Contrôle du Jeu")
    if st.button("Lancer les 2 dés 🎲", use_container_width=True):
        d1, d2, total, cat = roll_dice()
        st.session_state.history.append({'Dé 1': d1, 'Dé 2': d2, 'Total': total, 'Catégorie': cat})
        
        st.metric(label="Résultat du Lancer (Total)", value=str(total), delta=cat)
        st.write(f"Détails : Dé 1 = **{d1}** | Dé 2 = **{d2}**")

    if st.button("Réinitialiser l'historique", type="secondary"):
        st.session_state.history = []
        st.rerun()

with col2:
    st.header("📊 Statistiques en Direct")
    if st.session_state.history:
        df_current = pd.DataFrame(st.session_state.history)
        
        # Fréquences courantes
        counts = df_current['Catégorie'].value_counts(normalize=True) * 100
        categories_all = ["Moins de 7", "Égal à 7", "Plus de 7"]
        frequencies = [counts.get(cat, 0.0) for cat in categories_all]
        
        fig_bars = px.bar(
            x=categories_all, 
            y=frequencies, 
            labels={'x': 'Catégorie', 'y': 'Fréquence (%)'},
            title="Répartition Réelle Observée (%)",
            color=categories_all,
            color_discrete_map={"Moins de 7": "#E74C3C", "Égal à 7": "#F1C40F", "Plus de 7": "#2ECC71"}
        )
        fig_bars.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_bars, use_container_width=True)
        
        # Estimation Prochain Lancer
        st.subheader("💡 Estimation Expérimentale du Prochain Lancer")
        top_cat = counts.idxmax()
        st.info(f"**Tendance algorithmique basée sur vos lancers :** Privilégier temporairement **{top_cat}** *(Fiabilité : Basse - Hasard pur)*")
    else:
        st.info("Lancez les dés pour commencer à collecter des statistiques en direct.")

st.markdown("---")

# --- ZONE 2 : MODULE DE TEST DE MASSE & CONVERGENCE ---
st.header("🧪 Banc d'Essai : Simulations de Masse (100, 500, 1 000 lancers)")
st.write(
    "Ce module permet de tester la précision d'une approche statistique standard sur de larges volumes. "
    "Vous constaterez graphiquement que les résultats convergent inévitablement vers les probabilités théoriques strictes."
)

if st.button("Démarrer le Crash Test de Précision", type="primary", use_container_width=True):
    sim_sizes = [100, 500, 1000]
    accuracy_results = []
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    cols = [col_sim1, col_sim2, col_sim3]
    
    for idx, size in enumerate(sim_sizes):
        freqs, acc, df_sim = run_mass_simulation(size)
        accuracy_results.append(acc)
        
        with cols[idx]:
            st.subheader(f"📊 Série de {size} lancers")
            st.write(f"• Moins de 7 : **{freqs.get('Moins de 7', 0)*100:.1f}%**")
            st.write(f"• Égal à 7 : **{freqs.get('Égal à 7', 0)*100:.1f}%**")
            st.write(f"• Plus de 7 : **{freqs.get('Plus de 7', 0)*100:.1f}%**")
            st.metric(label="Taux de réussite de l'estimation", value=f"{acc:.2f}%")

    # Graphique de convergence de précision
    st.subheader("📈 Évolution de la Précision en fonction du Volume")
    df_acc = pd.DataFrame({
        'Volume de Lancers': ['100 Lancers', '500 Lancers', '1000 Lancers'],
        'Précision Observée (%)': accuracy_results
    })
    
    fig_line = px.line(
        df_acc, 
        x='Volume de Lancers', 
        y='Précision Observée (%)', 
        markers=True,
        title="Convergence Mathématique"
    )
    fig_line.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_line, use_container_width=True)
    
