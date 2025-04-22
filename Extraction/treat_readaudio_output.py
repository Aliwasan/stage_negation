import argparse
import sys
import os
import read_audiofile_prompt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utils'))
import manip_csv
    
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
	parser.add_argument("nom_debat", help = "nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	chemin_transcript = f"../output/ph_neg/{nom_debat}/{nom_debat}_txt/"
	chemin_audio = f"../output/ph_neg/{nom_debat}/{nom_debat}_audio/"
	list_ph_corr, list_ph_non_neg = read_audiofile_prompt.read_audiofile(chemin_transcript, chemin_audio)
	chemin_fichier_csv = "../output/csv/"
	nom_fichier_csv = nom_debat+'.csv'

	if list_ph_non_neg != []:
		# TODO enlever ph de la liste du csv réindexer
		print(list_ph_non_neg)
	else:
		while True:
			i = input("- Ajout d'une nouvelle colonne dans le csv existant, taper 'A' + Enter,\n\
						- Ajout de la liste à partir d'un index dans la colonne existante taper 'I' + Enter,\n\
						- Pour obtenir la liste seule de phrases corrigées taper 'L' + Enter\n\
						- Enfin pour quitter sans rien faire, taper 'q' + Enter :\t")
			if i == "A":
				i2 == input("Taper le nom de la col à ajouter au csv :\t")
				if isinstance(str, i2):
					manip_csv.add_col_to_csv(chemin_fichier_csv, nom_fichier_csv, list_ph_corr, i2)
			if i == 'I':
				print(list_ph_corr)
				i2 = input("Taper le n° de la première phrase à insérer + Enter, sinon faites Enter pour sortir :\t")
				if isinstance(int, i2):
					manip_csv.add_in_col_to_csv(chemin_fichier_csv, nom_fichier_csv, list_ph_corr, i2)
				else:
					break
			elif i == 'L':
				print(list_ph_corr)
				break
			elif i == "q":
				break
			else:
				continue
