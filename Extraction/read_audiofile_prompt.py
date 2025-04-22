from pydub import AudioSegment
from pydub.playback import play
import sys
import os
import glob
from glob import glob
import argparse

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
	prompt_phrase = prompt(f"Modifier : {phrase}:	 ", default=phrase, key_bindings=kb)
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
	list_ph_non_neg = []
	while True:
		try:
			i = input("\nEntrez le n° de la phrase négative à écouter\n\
			 		'Enter' pour écouter les phrases à partir du début et les suivantes.\n\
			 		'q' + 'Enter' pour quitter : ")
			if i.isdigit():
				cpteur = int(i)
				for transcript, audio in zip(list_transcripts[cpteur-1:], list_audio[cpteur-1:]):
					with open(transcript) as f:
						print(f"Phrase négative n° {cpteur} :\n")
						phrase = f.readline()
						print(phrase + "\n\n")
						sound = AudioSegment.from_file(audio, format="mp3")
						play(sound)
						s = input("Répéter : taper 'r' + 'Enter',\n\
								- Modifier et valider : taper 'm',\n\
								- Enlever de la liste car pas de négation : taper 'e',\n\
								- Lire les phrases suivantes : taper 'Enter', \n\
								- Quitter : taper 'q'")
						if s == "r":
							play(sound)
							s = input("- Modifier et valider : taper 'm',\n\
								- Enlever de la liste car pas de négation : taper 'e',\n\
								- Lire les phrases suivantes : taper 'Enter'")
							if s == "m":
								list_ph_corr.append(modif_phrase(cpteur, phrase))
								cpteur+=1
							elif s == "e":
								list_ph_non_neg.append((cpteur, phrase))
								cpteur+=1
							else:
								cpteur+=1
								continue
						elif s == "e":
								list_ph_non_neg.append((cpteur, phrase))
								cpteur+=1
						elif s == "m":
							list_ph_corr.append(modif_phrase(cpteur, phrase))
							cpteur +=1
						elif s == "q":
							break
						else:
							cpteur +=1
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
						s = input("- Répéter : taper 'r' + 'Enter',\n\
								- Modifier et valider : taper 'm',\n\
								- Enlever de la liste car pas de négation : taper 'e',\n\
								- Lire les phrases suivantes : taper 'Enter'\n\
								- Sortir : taper q + 'Enter'\n\t")
						if s == "r":
							play(sound)
							s = input("- Modifier et valider : taper 'm',\n\
									- Enlever de la liste car pas de négation : taper 'e',\n\
									- Lire les phrases suivantes : taper 'Enter'\n\t")
							if s == "m":
								list_ph_corr.append(modif_phrase(cpteur, phrase))
							elif s == "e":
								list_ph_non_neg.append((cpteur, phrase))
							else:
								continue
						elif s == 'm':
							list_ph_corr.append(modif_phrase(cpteur, phrase))
						elif s == "e":
								list_ph_non_neg.append((cpteur, phrase))  
						elif s == "q":
							break
						else:
							continue
		except Exception as e:
			print(f"Error : {e}")
		# except TypeError as te: # si on a pas de phrases validées et que l'on break
		# 	print(f"TypeError : {te}")
		 
	print(f"list_ph_corr : {list_ph_corr}")
	print(f"list_phrases_non_neg : {list_ph_non_neg}")
	return list_ph_corr, list_ph_non_neg
	
