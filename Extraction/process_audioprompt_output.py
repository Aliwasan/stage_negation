import argparse
import sys
import os

from prompt_toolkit.shortcuts import choice
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

import read_audiofile_prompt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utils'))
import manip_csv # type: ignore
import update_csv
    
""" Exécution de la fonction read_audiofile() 
	appel à la fonction de maj du csv
	retourne un csv maj avec la col phrase_corrigee
"""

def choix():
	style = Style.from_dict(
    {
        "frame.border": "#F1E61B",
        "selected-option": "bold",
    }
	)
	i = choice(
				message = HTML("<u>Action sur la liste de phrases corrigées :</u>"),
				options=[
					("A", "Ajout d'une partie seulement des phrases corrigées dans la colonne 'phrase_corrigee' du csv existant"),
					("B", "Ajout de l'ensemble des phrases du débat, nouvelle colonne 'phrase_corrigee' dans le .csv existant"),
					("C", "Imprimer uniquement la liste de phrases corrigées, sans action sur le .csv"),
					("Q", "quitter")
				],
				default="Q",
				style=style,
				show_frame=True
			)
	return i

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
	parser.add_argument("nom_debat", help = "nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	chemin_transcript = f"../output/ph_neg/{nom_debat}/{nom_debat}_txt/"
	chemin_audio = f"../output/ph_neg/{nom_debat}/{nom_debat}_audio/"
	list_ph_corr = read_audiofile_prompt.read_audiofile(chemin_transcript, chemin_audio, nom_debat)
	chemin_fichier_csv = "../output/csv/"
	nom_fichier_csv = nom_debat+'.csv'
	
	while True:
		i = choix()
		if i == "A":
			updated_df = update_csv.update_df_on_idx_horo_list(chemin_fichier_csv, nom_debat, list_ph_corr)
			#TODO	ajouter les phrases corrigées en fonction de l'idx_horo dans la colonne 'phrase_corrigee' déjà remplie en partie dan sle .csv existant
			# manip_csv.filtered_df(chemin_fichier_csv, nom_debat, 'phrase_corrigee', 'N/A') # filtre ce qui n'est pas N/A
			# df = manip_csv.drop_col(chemin_fichier_csv, nom_debat, 'n_ph')
			# manip_csv.reindexe_df(chemin_fichier_csv, nom_debat, df)
		elif i == "B":
			updated_df = update_csv.update_df_on_idx_horo_list(chemin_fichier_csv, nom_debat, list_ph_corr)
			manip_csv.df_to_csv(chemin_fichier_csv, nom_debat, updated_df)
		elif i == 'C':
			print(list_ph_corr)
			break
		elif i == "Q":
			break
		else:
			continue

# TODO : fonction qui recrée un rep : un fichier par ph corrigée avec nom fichier 'idx_horo' : modèle dans make_data()
# with open(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_txt/{e['idx_horo']}_{nom_debat}.txt", "w") as f_out:
# 				f_out.write(e['sent'])