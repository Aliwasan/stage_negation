from pydub import AudioSegment
from pydub.playback import play
import glob
from glob import glob
import argparse
import polars as pl
from utils import df_to_csv

from prompt_toolkit import prompt, Application
from prompt_toolkit.key_binding import KeyBindings


def num_fichier(chemin_fichier: str):
	""" Retourne au format int le numéro au format string au début du nom de fichier """
	return int(chemin_fichier.split('/')[-1].split('_')[0])

def modif_phrase(n_ph: str, phrase: str):
	""" Lance le prompt
		crée un binding pour les touches du clavier
		(optionnel mais peut être utile pour personnaliser l'édition)
	"""
	kb = KeyBindings()
	prompt_phrase = prompt(f"Modifier : {phrase}:     ", default=phrase, key_bindings=kb)
	nouvelle_phrase = (n_ph, prompt_phrase)
	return nouvelle_phrase

def add_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_ph_corr: list, start_index=None):
	""" Insère une colonne de donnée d'un df à un fichier csv préexistant:
		début de correction des phrases d'un débat.
		ou
		Insère des données dans une colonne spécifique à partir d'un index de rang donné: 
		suite de la correction des phrases d'un débat.
	"""
	list_ph = [p[1] for p in list_ph_corr]
	df = pl.read_csv(chemin_fichier_csv + nom_fichier_csv)

	print(f"Taille du DataFrame: {df.height}")
	print(f"Taille de la liste des phrases: {len(list_ph)}")

	
	if start_index != None: # si on a un index c'est que l'on veut reprendre une correction
		# Vérifier si la colonne cible existe
		if 'phrase_corrigee' not in df.columns:
			raise ValueError(f"La colonne 'phrase_corrigee' n'existe pas dans le DataFrame.")		
		# Vérifier que la longueur des nouvelles données est compatible avec l'index de départ
		if start_index >= df.height:
			raise ValueError("L'index de départ est supérieur à la hauteur du DataFrame.")
		
		# création de la Series avec les données à insérer
		s = pl.Series("phrase_corrigee", list_ph, strict=False)

		# Modifier la colonne existante à partir du rang donné
		# Faire une liste avec la col existante
		to_update_column = df['phrase_corrigee'].to_list()
		# print(to_update_column)

		# Insérer les nouvelles données à partir du rang spécifié
		# rappel les rangs commencent bien à 1
		start_index -= 1 # car on est dans une liste donc index commence à 0
		to_update_column[start_index:start_index + len(list_ph)] = list_ph
		print(f"len de la nouvelle colonne :{len(to_update_column)}")

		# Créer un nouveau DataFrame avec la colonne modifiée
		# -> vérifier que la nouvelle liste est plus courte que le df, on la complète avec des valeurs None
		# if len(to_update_column) < df.height:
		# 	list_ph.extend([None] * (df.height - len(to_update_column)))

		df = df.with_columns(pl.Series('phrase_corrigee', to_update_column))
		print(f"df après ajout de phrases corrigée dans l'existant :\n {df}")

	else: # pas d'index : on commence la correction d'un nouveau débat
		
		# Si list_ph est plus courte que le DataFrame, on la complète avec des valeurs None
		if len(list_ph) < df.height:
			list_ph.extend([None] * (df.height - len(list_ph)))
		s = pl.Series("phrase_corrigee", list_ph, strict=False)
		df.insert_column(3, s) # on insère la col après la col ph_neg transcrites
		print(f"df nouveau débat :\n {df}")

	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplacera le précédent le cas échéant
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return


def read_audiofile(chemin_rep_transcript: str, chemin_rep_audio: str):
	""" Ouvre simultanément :
	 - le fichier de la phrase négative transcrite, l'affiche sur le Terminal
	 - le fichier du segment audio correspondant et le lit
	 ouvre un prompt permettant de modifier la phrase
	 renvoie la liste des phrases à entrer dans la colonne phrase corrigée du df, csv
	""" 
	list_transcripts = glob(chemin_rep_transcript + '/*.txt')
	list_transcripts.sort(key=num_fichier)
	# print(list_transcripts)
	list_audio = glob(chemin_rep_audio + '/*.mp3')
	list_audio.sort(key=num_fichier)
	# print(list_audio)

	list_ph_corr = []
	while True:
		try:
			i = input("\nEntrez le n° de la phrase négative à écouter\n\
			 		'Enter' pour écouter les phrases à partir du début et les suivantes.\n\
			 		'q' + 'Enter' pour quitter : ")
			if i.isdigit():
				cpteur = int(i)
				print(list_transcripts[cpteur-1])
				with open(chemin_rep_transcript+list_transcripts[cpteur-1].split('/')[-1]) as f:
					print(f"Phrase négative n° {cpteur} :\n")
					phrase = f.readline()
					print(phrase + "\n\n")
					sound = AudioSegment.from_file(chemin_rep_audio+list_audio[cpteur-1].split('/')[-1], format="mp3")
					play(sound)
					s = input("Taper sur 'r' + entrée pour répéter, 'm' pour modifier et valider, 'Enter' pour les phrases suivantes, 'q' + entrée pour sortir : ")
					if s == "r":
						play(sound) # si je met pass ou continue reste sur le play(sound) de la phrase courante
					elif s == "m":
						list_ph_corr.append(modif_phrase(cpteur, phrase))
						# ici il faut un input pour passer à la boucke for
						s = input("'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
						if s == "q":
							break
						else:
							cpteur = cpteur+1 # problème ici il faut g
							for transcript, audio in zip(list_transcripts[cpteur-1:], list_audio[cpteur-1:]):
								with open(transcript) as f_suite:
									print(f"Phrase négative n° {cpteur} :\n")
									phrase = f_suite.readline()
									print(phrase + "\n\n")
									sound = AudioSegment.from_file(audio, format="mp3")
									play(sound)
									s = input("'r' + 'Enter' pour répéter et continuer, 'm' pour modifier et valider, 'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
									if s == "r":
										play(sound)
										continue
									elif s == "m":
										list_ph_corr.append(modif_phrase(cpteur, phrase))
										cpteur = cpteur+1
									elif s == "q":
										break
									else:
										continue
					elif s == "q":
						break
					else:
						continue
							
			elif i == "q":
						break
			else:
				cpteur = 0
				for transcript, audio in zip(list_transcripts, list_audio):
					with open(transcript) as f:
						cpteur += 1
						print(f"Phrase négative n° {cpteur} :\n")
						phrase = f.readline()
						print(phrase + "\n\n")
						sound = AudioSegment.from_file(audio, format="mp3")
						play(sound)
						s = input("'r' + 'Enter' pour répéter, 'm' pour modifier et valider, 'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
						if s == "r":
							play(sound)
							break # si continue répète et lit la phrase suivante
						elif s == 'm':
							list_ph_corr.append(modif_phrase(cpteur, phrase))
						elif s == "q":
							break
						else:
							continue
		except Exception as e:
			print(f"Error : {e}")
	print(list_ph_corr)
	print(len(list_ph_corr))
	return list_ph_corr

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
	parser.add_argument("nom_debat", help = "nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	chemin_transcript = f"../output/ph_neg/{nom_debat}/{nom_debat}_txt/"
	chemin_audio = f"../output/ph_neg/{nom_debat}/{nom_debat}_audio/"
	list_ph_corr = read_audiofile(chemin_transcript, chemin_audio)
	chemin_fichier_csv = "../output/csv/"
	nom_fichier_csv = nom_debat+'.csv'
	df = add_to_csv(chemin_fichier_csv, nom_fichier_csv, list_ph_corr, start_index=11)
	# print(df)