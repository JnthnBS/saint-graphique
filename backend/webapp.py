from flask import jsonify,request,send_file, Flask
import io
import base64
import dash
from dash import Dash, Input, Output, callback, html, dcc
import pandas as pd
from flask_cors import CORS
import plotly.express as px
from plotly import graph_objects as go
import re
import os
import random
# Initialisation de l'app Dash (sans layout)
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  
CORS(server)  
# --- Layout de l'application ---
app.layout = html.Div([
])    
# Fonctions
## Chargement des données
def donnees_pop(annee):
    pcs = pd.read_csv(os.path.join("data", f"{annee}_population", "PCS.csv"), sep=";", dtype={"PCS":str, "NB" : float, "SEXE": str}, low_memory=False)        
    revenus = pd.read_csv(os.path.join("data", f"{annee}_population", "revenus.csv"), sep=";", dtype={"PCS":str})
    diplomes = pd.read_csv(os.path.join("data", f"{annee}_population", "diplomes.csv"), sep=";", dtype={"PCS":str})
    labels = pd.read_csv(os.path.join("data", "labels_2.csv"), sep=";", dtype={"PCS":str})
    return pcs, revenus, diplomes, labels

def donnees_elec(annee, objet):
    communes = pd.read_csv(os.path.join("data", f"{annee}_{objet}", "communes.csv"), sep=";", low_memory=False)
    compositions = pd.read_csv(os.path.join("data", f"{annee}_{objet}", "compositions.csv"), sep=";", dtype={"PCS": str})
    couleurs = pd.read_csv(os.path.join("data", f"{annee}_{objet}", "couleurs.csv"), sep=";")
    labels = pd.read_csv(os.path.join("data", "labels_1.csv"), sep=";", dtype={"PCS":str})
    return communes, compositions, couleurs, labels
## Opérations sur la population
def effectifs(pcs, geo, sexe, df_codes):
    if str(geo) == "100":
        df_filtre = pcs
    else:
        df_filtre = pcs[pcs["CODGEO"] == str(geo)]
    if sexe == 1:
        result = df_filtre.groupby("PCS")["NB"].sum().reset_index()
        result["sexe"] = "Tous"
    elif sexe == 2:
        result = df_filtre[df_filtre["SEXE"] == "1"].groupby("PCS")["NB"].sum().reset_index()
        result["sexe"] = "Hommes"
    elif sexe == 3:
        result = df_filtre[df_filtre["SEXE"] == "2"].groupby("PCS")["NB"].sum().reset_index()
        result["sexe"] = "Femmes"
    else:
        print("Option invalide")
    total_effectifs = result['NB'].sum()
    result['Part'] = (result['NB'] / total_effectifs) * 100
    libgeo = df_codes[df_codes["CODGEO"] == geo]["LIBGEO"].values[0]
    result["LIBGEO"] = libgeo
    return result

def abscisses(df):
    df["Score"] = (df["Patrimoine"] / df["Niveau de vie"]) * 100
    df_sorted = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df_sorted["Rang"] = df_sorted.index + 1  
    df_sorted["X"] = -10 + (20 / 29) * (30 - df_sorted["Rang"])
    result =  df_sorted[["PCS", "X"]]
    return result

def ordonnees(df):
    df["Score"] = (
        5 * df["5"] + 
        3 * df["3"] + 
        2 * df["2"] + 
        df["BAC"] -   
        df["CAP"] -   
        2 * df["BREVET"] -
        3 * df["CERTIF"]  
    )
    df_sorted = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df_sorted["Rang"] = df_sorted.index + 1  
    df_sorted["Y"] = -10 + (20 / 29) * (30 - df_sorted["Rang"])
    result =  df_sorted[["PCS", "Y"]]
    return result

def coordonnees_population(labels,effectifs,abscisses,ordonnees):
    df = pd.merge(labels,effectifs, on="PCS", how="inner")
    df = pd.merge(df, abscisses, on="PCS", how="inner")
    df = pd.merge(df, ordonnees, on="PCS", how="inner")
    df = df.rename(columns={"NB": "Effectifs", "LABELS": "Labels"})
    X_b = (df['Effectifs'] * df['X']).sum() / df['Effectifs'].sum()
    Y_b = (df['Effectifs'] * df['Y']).sum() / df['Effectifs'].sum()
    bary = {
        "PCS": "100",
        "Labels": "Barycentre de la population",
        "Effectifs": 0,
        "sexe": df["sexe"].iloc[1],
        "Part": 50,
        "LIBGEO": df["LIBGEO"].iloc[0],
        "X": X_b,
        "Y": Y_b,
        "PCS_Labels": "100 - Barycentre de la population"
        }
    barycentre = pd.DataFrame([bary])    
    df["PCS_Labels"] = df["PCS"] + " - " + df["Labels"]
    return df, barycentre
## Opérations sur les électorats
def simplification_pcs(df, labels):
    df["PCS"] = df["PCS"].astype(str).str[0]
    df['X_barycentre'] = df['Effectifs'] * df['X']
    df['Y_barycentre'] = df['Effectifs'] * df['Y']
    df['Somme_X'] = df.groupby('PCS')['X_barycentre'].transform('sum')
    df['Somme_Y'] = df.groupby('PCS')['Y_barycentre'].transform('sum')
    df['Somme_Effectifs'] = df.groupby('PCS')['Effectifs'].transform('sum')
    df['Barycentre_X'] = df['Somme_X'] / df['Somme_Effectifs']
    df['Barycentre_Y'] = df['Somme_Y'] / df['Somme_Effectifs']
    result = df[['PCS', 'Barycentre_X', 'Barycentre_Y']].drop_duplicates()
    result = pd.merge(labels,result, on="PCS", how="inner")
    result = result.rename(columns={'Barycentre_X': 'X'})
    result = result.rename(columns={'Barycentre_Y': 'Y'})
    result = result.rename(columns={'LABELS': 'Labels'})
    return result

def barycentres_votes(df_barycentres,compositions):
    df_merged = df_barycentres.merge(compositions, on='PCS')
    candidats = compositions.columns[1:]
    barycentres = []
    for candidat in candidats:
        poids = df_merged[candidat]
        X = df_merged['X'] * poids
        Y = df_merged['Y'] * poids
        somme_X = X.sum()
        somme_Y = Y.sum()
        somme_poids = poids.sum()
        if somme_poids == 0:
            continue
        bary_X = somme_X / somme_poids
        bary_Y = somme_Y / somme_poids
        barycentres.append({
            'PCS': candidat,
            'Labels': candidat,
            'X': bary_X,
            'Y': bary_Y,
            'Effectifs': somme_poids
        })
    df_barycentres = pd.DataFrame(barycentres)
    return df_barycentres

def votes(df, suffrages, codeGeo, couleurs, df_codes, annee):
    df_filtre = suffrages[suffrages["CODGEO"] == str(codeGeo)]
    suffrages_pivot = df_filtre.melt(id_vars=['CODGEO', 'LIBGEO'],
                     var_name='Labels',
                     value_name='Effectifs')
    labels_df = df['Labels'].tolist()
    suffrages_pivot = suffrages_pivot[suffrages_pivot['Labels'].isin(labels_df)]
    df_final = df.merge(suffrages_pivot, on='Labels', suffixes=('_old', '_new'))
    df_final['Effectifs'] = df_final['Effectifs_new']
    total_effectifs = df_final['Effectifs'].sum()
    df_final['Part'] = (df_final['Effectifs'] / total_effectifs) * 100
    result = df_final[['PCS', 'Labels', 'Effectifs', 'Part', 'X', 'Y']]
    result = pd.merge(result,couleurs, on="Labels", how="inner")
    libgeo = df_codes[df_codes["CODGEO"] == codeGeo]["LIBGEO"].values[0]
    result["LIBGEO"] = libgeo
    result["Annee"] = annee
    return result
## Opérations sur le graphique
def ajout_calque_pop(fig, df, geo, barycentre):
    palettes = [["#B03719", "#FD4E23"], ["#19ADB0", "#23FAFC"], ["#19B05D", "#23FC85"], ["#B09919", "#FCDC23"], ["#5819B0", "#7E23FC"]]
    colormap = random.choice(palettes)
    if df["PCS"].dtype == 'object':  # Si c'est du texte
        df["PCS"] = df["PCS"].astype('category').cat.codes
    if barycentre["PCS"].dtype == 'object':  # Si c'est du texte
        barycentre["PCS"] = barycentre["PCS"].astype('category').cat.codes
    fig.add_trace(
        go.Scatter(
            x=df["X"],
            y=df["Y"],
            mode="markers",
            marker= dict(
                size=df["Part"],
                sizeref=0.02,
                sizemode='area',
                symbol="circle",
                color=df["PCS"],
                colorscale=colormap),
            text=df["PCS"],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "%{customdata[3]:.2f} %<br>" +
                "<b>Effectifs:</b> %{customdata[1]:.0f}<br>" +
                "<b>%{customdata[2]}</b> - %{customdata[4]}<br>" +
                "<extra></extra>"
            ),
            customdata=df[['PCS_Labels','Effectifs','LIBGEO', 'Part', 'sexe']],
            hoverinfo="text"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=barycentre["X"],
            y=barycentre["Y"],
            mode="markers",
            marker= dict(
                size=barycentre["Part"],
                sizeref=0.02,
                sizemode='area',
                symbol="circle-open-dot",
                color=barycentre["PCS"],
                colorscale=colormap),
            text=barycentre["PCS"],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "<b>%{customdata[2]}</b> - %{customdata[4]}<br>" +                
                "<extra></extra>"
            ),
            customdata=barycentre[['PCS_Labels','Effectifs','LIBGEO', 'Part', 'sexe']],
            hoverinfo="text"
        )
    )
    
def ajout_calque_elec(fig, df, geo):
    fig.add_trace(
        go.Scatter(
            x=df["X"],
            y=df["Y"],
            mode="markers",
            marker= dict(
                size=df["Part"],
                sizeref=0.05,
                sizemode='area',
                symbol="diamond-dot",
                color=df["Couleurs"],),
            text=df["PCS"],
            hovertemplate=(
                "<b>Candidat %{customdata[2]}:</b> %{customdata[0]}<br>" +
                "<b>Score:</b> %{marker.size:.2f}%<br>" +
                "<b>%{customdata[1]}</b><br>" +
                "<extra></extra>"
            ),
            customdata=df[["PCS","LIBGEO","Annee"]],
            hoverinfo="text"
        )
    )

# Endpoints pour récupérer les données du graphique
@app.server.route('/api/graph', methods=['POST'])
def get_graph_data():
    # Récupération des données JSON
    requests = request.get_json()
    if not requests or not isinstance(requests, list):
        return jsonify({"error": "Données invalides : attendez une liste de dictionnaires"}), 400
    # Initialisation du graphique et de sa diagonale
    fig = go.Figure()
    fig.add_shape(type="line",
    xref="x", yref="y",
    x0=-10, y0=-10, x1=10, y1=10,
    layer="below",
    line=dict(
        color="LightGrey",
        dash="dot",
    ))
    # Création d'une trace pour chaque requête
    for req in requests:
        geo = req['commune']
        sexe = int(req['sexe'])
        objet = str(req['objet'])
        annee = str(req['annee'])
        # Il faut les coordonnées de la population
        if annee != "2022":
            annee_pop = "2022"
        elif annee == "2022":
            annee_pop = annee
        pcs, revenus, diplomes, labels_2 = donnees_pop(annee_pop)
        ensemble = effectifs(pcs, geo, sexe, df_codes)
        coordonnees_pop, barycentre_pop = coordonnees_population(labels_2, ensemble, abscisses(revenus), ordonnees(diplomes))
        # Affichage de la population si c'est la demande
        if objet == "population":
            ajout_calque_pop(fig, coordonnees_pop, geo, barycentre_pop)
        # Calcul des coordonnées des électorats et affichage si c'est la demande
        elif objet == "presidentielles" or objet == "legislatives" or objet == "europeennes":
            communes, compositions, couleurs, labels_1 = donnees_elec(annee,objet)
            pcs_1 = simplification_pcs(coordonnees_pop, labels_1)
            barycentres = barycentres_votes(pcs_1,compositions)
            coordonnees_votes = votes(barycentres, communes, geo, couleurs, df_codes, annee)
            ajout_calque_elec(fig, coordonnees_votes, geo)
    # Une fois toutes les traces générées, on génère le layout
    largeur = requests[0]["width"]
    if largeur > 900:
        largeur = 900
        hauteur = largeur
    elif largeur <= 900:
        hauteur = largeur
    fig.update_layout(
        width=largeur,
        height=hauteur,
        autosize=False,
        showlegend=False,
        xaxis_title="Exploitation",
        yaxis_title="Domination",
    )
    # Enfin, on exporte
    plotly_json = fig.to_json()
    return jsonify(plotly_json), 200, {'Content-Type': 'application/json'}
# Lancement de l'application
if __name__ == "__main__":
    app.run(host='0.0.0.0')
## On importe les data
df_codes = pd.read_csv("data/communes.csv", sep=";")
