from pydub import AudioSegment
from pydub.playback import play
import sys
import termios
import glob
from glob import glob
import argparse
from manip_csv import add_col_to_csv

from prompt_toolkit import prompt, Application
from prompt_toolkit.key_binding import KeyBindings




def vider_buffer():
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)

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


def read_audiofile(chemin_rep_transcript: str, chemin_rep_audio: str):
	""" Ouvre simultanément :
	 - le fichier de la phrase négative transcrite, l'affiche sur le Terminal
	 - le fichier du segment audio correspondant et le lit
	 ouvre un prompt permettant de modifier la phrase
	 renvoie la liste des phrases à entrer dans la colonne phrase corrigée du df, csv
	""" 
	list_transcripts = glob(chemin_rep_transcript + '/*.txt')
	# print(list_transcripts)
	list_transcripts.sort(key=num_fichier)
	
	list_audio = glob(chemin_rep_audio + '/*.mp3')
	list_audio.sort(key=num_fichier)
	# print(list_audio)

	list_ph_corr = []
	while True:
		try:
			# vider_buffer()
			i = input("\nEntrez le n° de la phrase négative à écouter\n\
			 		'Enter' pour écouter les phrases à partir du début et les suivantes.\n\
			 		'q' + 'Enter' pour quitter : ")
			if i.isdigit():
				cpteur = int(i)
				for transcript, audio in zip(list_transcripts[cpteur-1:], list_audio[cpteur-1:]):
					# print(transcript)
					# print(audio)
					with open(transcript) as f:
						print(f"Phrase négative n° {cpteur} :\n")
						phrase = f.readline()
						print(phrase + "\n\n")
						sound = AudioSegment.from_file(audio, format="mp3")
						play(sound)
						s = input("'r' + 'Enter' pour répéter et continuer, 'm' pour modifier et valider, 'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
						if s == "r":
							play(sound)
							s = input("'m' pour modifier et valider, 'Enter' pour les phrases suivantes")
							if s == "m":
								list_ph_corr.append(modif_phrase(cpteur, phrase))
								cpteur +=1
							else:
								cpteur += 1
								continue
						elif s == "m":
							list_ph_corr.append(modif_phrase(cpteur, phrase))
							cpteur = cpteur+1
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
							s = input("'m' pour modifier et valider, 'Enter' pour les phrases suivantes")
							if s == "m":
								list_ph_corr.append(modif_phrase(cpteur, phrase))
								cpteur +=1
							else:
								cpteur += 1
								continue
						elif s == 'm':
							list_ph_corr.append(modif_phrase(cpteur, phrase))
						elif s == "q":
							break
						else:
							continue
		except Exception as e:
			print(f"Error : {e}")
		# except TypeError as te: # si on a pas de phrases validées et que l'on break
		# 	print(f"TypeError : {te}")
		 
	print(list_ph_corr)
	print(len(list_ph_corr))
	print(type(list_ph_corr))
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
	while True:
		i = input("Ajout ou écrasement de la colonne 'phrase_corrigee dans le csv ? Vérifier les index le cas échéant.\n\
			 Si oui taper 'o' + Enter, pour quitter sans faire de csv taper 'q' + Enter : \t")
		if i=="o":
			add_col_to_csv(chemin_fichier_csv, nom_fichier_csv, list_ph_corr, 448)
			break
		elif i=="q":
			break
		else:
			continue