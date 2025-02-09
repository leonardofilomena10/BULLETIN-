import streamlit as st
import json

# Chargement de la configuration depuis le fichier JSON
with open("config.json", "r") as f:
    config = json.load(f)

st.title("Simulateur Interactif de Bulletin de Paie")

st.markdown("### 1. Paramètres de Base")
salaire_base_taux = st.number_input("Taux horaire de base (€)", value=config["salaire_base_taux"])
heures_base = st.number_input("Nombre d'heures de base", value=config["heures_base"])
coef_revalorisation = st.number_input("Coefficient de revalorisation", value=config["coef_revalorisation"])

st.markdown("### 2. Éléments Variables")
# Heures supplémentaires à 125%
heures_sup_125 = st.number_input("Heures supplémentaires à 125%", value=config["maj_125"]["heures"])
taux_sup_125 = st.number_input("Taux horaire HS 125% (€)", value=config["maj_125"]["taux"])

# Heures dominicales
heures_dimanche = st.number_input("Heures travaillées le dimanche", value=config["dimanche"]["heures"])
maj_dimanche = st.number_input("Majoration dimanche (€)", value=config["dimanche"]["majoration"])

# Heures de nuit à 8%
heures_nuit_8 = st.number_input("Heures de nuit à 8%", value=config["nuit_8"]["heures"])
supp_nuit_8 = st.number_input("Supplément pour nuit à 8% (€)", value=config["nuit_8"]["supp"])

# Heures de nuit à 20%
heures_nuit_20 = st.number_input("Heures de nuit à 20%", value=config["nuit_20"]["heures"])
supp_nuit_20 = st.number_input("Supplément pour nuit à 20% (€)", value=config["nuit_20"]["supp"])

# Habillage/déshabillage
heures_habillage = st.number_input("Heures d'habillage/déshabillage", value=config["habillage"]["heures"])
taux_habillage = st.number_input("Taux habillage (€)", value=config["habillage"]["taux"])

# Rappel de salaire
rappel = st.number_input("Rappel de salaire (€)", value=config["rappel"])

# Absence non payée
heures_absence = st.number_input("Heures d'absence non payées", value=config["absence"]["heures"])
taux_absence = st.number_input("Taux absence (€)", value=config["absence"]["taux"])

# Indemnité entretien
indemnite_entretien = st.number_input("Indemnité d'entretien (€)", value=config["indemnite_entretien"])

st.markdown("### 3. Calcul du Salaire Brut")

# Calcul du salaire de base (avec revalorisation)
salaire_base = heures_base * salaire_base_taux * coef_revalorisation

# Calcul des éléments variables avec revalorisation
sup_125 = heures_sup_125 * taux_sup_125 * coef_revalorisation
dimanche = heures_dimanche * maj_dimanche * coef_revalorisation
nuit_8 = supp_nuit_8 * coef_revalorisation
nuit_20 = supp_nuit_20 * coef_revalorisation
habillage = heures_habillage * taux_habillage * coef_revalorisation
absence = heures_absence * taux_absence * coef_revalorisation

# On ajoute rappel et on retranche l'absence
brut_total = salaire_base + sup_125 + dimanche + nuit_8 + nuit_20 + habillage + (rappel * coef_revalorisation) - absence

st.write(f"**Salaire de base :** {salaire_base:.2f} €")
st.write(f"**Heures sup 125% :** {sup_125:.2f} €")
st.write(f"**Heures dominicales :** {dimanche:.2f} €")
st.write(f"**Nuit 8% :** {nuit_8:.2f} €")
st.write(f"**Nuit 20% :** {nuit_20:.2f} €")
st.write(f"**Habillage :** {habillage:.2f} €")
st.write(f"**Rappel :** {rappel * coef_revalorisation:.2f} €")
st.write(f"**Absence non payée :** {-absence:.2f} €")
st.markdown(f"**→ Salaire brut total : {brut_total:.2f} €**")

st.markdown("### 4. Calcul des Cotisations Salariales")

cot = config["cotisations"]

# Santé
sante = cot["sante"] * brut_total
# Complémentaire santé sur base fixe
complementaire_sante = config["base_complementaire_sante"] * cot["complementaire_sante"]
# Invalidité/Décès
invalidite = cot["invalidite_deces"] * brut_total
# Retraite
retraite_plaf = cot["retraite_plafonnee"] * brut_total
retraite_deplaf = cot["retraite_deplafonnee"] * brut_total
# Complémentaire tranche 1
compl_tranche1 = cot["complementaire_tranche1"] * brut_total
# CSG/CRDS (on reprend la base ajustée de l'exemple d'origine : brut - 17.47 * coef)
base_csg = brut_total - (17.47 * coef_revalorisation)
csg_deduc = cot["csg_deductible"] * base_csg
csg_nondeduc = cot["csg_non_deductible"] * base_csg
# Supplément heures sup non déductible (appliqué sur la partie HS d'origine)
cs_sup = cot["cs_sup_hours"] * (sup_125 / coef_revalorisation)

total_cot_sal = sante + complementaire_sante + invalidite + retraite_plaf + retraite_deplaf + compl_tranche1 + csg_deduc + csg_nondeduc + cs_sup

st.write(f"Santé : {sante:.2f} €")
st.write(f"Complémentaire santé : {complementaire_sante:.2f} €")
st.write(f"Invalidité/Décès : {invalidite:.2f} €")
st.write(f"Retraite plafonnée : {retraite_plaf:.2f} €")
st.write(f"Retraite déplafonnée : {retraite_deplaf:.2f} €")
st.write(f"Complémentaire Tranche 1 : {compl_tranche1:.2f} €")
st.write(f"CSG/CRDS déductible : {csg_deduc:.2f} €")
st.write(f"CSG/CRDS non déductible : {csg_nondeduc:.2f} €")
st.write(f"Supplément HS non déductible : {cs_sup:.2f} €")
st.markdown(f"**→ Total Cotisations Salariales : {total_cot_sal:.2f} €**")

st.markdown("### 5. Calcul du Net et de l'Impôt")

net_avant_impot = brut_total - total_cot_sal + indemnite_entretien
st.write(f"Net avant impôt : {net_avant_impot:.2f} €")

# Calcul du prélèvement à la source avec taux réel
taux_impot = config["taux_impot"]
impot = taux_impot * net_avant_impot
net_final = net_avant_impot - impot

st.write(f"Prélèvement à la source ({taux_impot*100:.1f}%) : {impot:.2f} €")
st.markdown(f"**→ Salaire net final : {net_final:.2f} €**")

st.markdown("### 6. Cotisations Patronales et Coût Total Employeur")

cp = config["cotisations_patronales"]

sante_pat = config["base_complementaire_sante"] * cp["sante"]
retraite_plaf_pat = cp["retraite_plafonnee"] * brut_total
retraite_deplaf_pat = cp["retraite_deplafonnee"] * brut_total
invalidite_pat = cp["invalidite_deces"] * brut_total
accidents = cp["accidents_travail"] * brut_total
chomage = cp["chomage"] * brut_total
compl_tranche1_pat = cp["complementaire_tranche1"] * brut_total
allocations = cp["allocations_familiales"] * brut_total
autres = cp["autres"]

total_cot_pat = (sante_pat + retraite_plaf_pat + retraite_deplaf_pat + invalidite_pat +
                 accidents + chomage + compl_tranche1_pat + allocations + autres)

st.write(f"Santé (patronale) : {sante_pat:.2f} €")
st.write(f"Retraite plafonnée (patronale) : {retraite_plaf_pat:.2f} €")
st.write(f"Retraite déplafonnée (patronale) : {retraite_deplaf_pat:.2f} €")
st.write(f"Invalidité/Décès (patronale) : {invalidite_pat:.2f} €")
st.write(f"Accidents du travail : {accidents:.2f} €")
st.write(f"Chômage (patronale) : {chomage:.2f} €")
st.write(f"Complémentaire Tranche 1 (patronale) : {compl_tranche1_pat:.2f} €")
st.write(f"Allocations familiales : {allocations:.2f} €")
st.write(f"Autres contributions : {autres:.2f} €")
st.markdown(f"**→ Total Cotisations Patronales : {total_cot_pat:.2f} €**")

allègement = config["allègement_taux"] * brut_total
cout_total_employeur = brut_total + total_cot_pat - allègement

st.write(f"Allègement de charges : {allègement:.2f} €")
st.markdown(f"**→ Coût Total Employeur : {cout_total_employeur:.2f} €**")
