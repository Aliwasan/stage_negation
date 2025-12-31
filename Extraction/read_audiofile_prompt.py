from pydub import AudioSegment
from pydub.playback import play
import re
import glob
from glob import glob
from colorama import Style as colorstyle
from colorama import Fore, Back

from prompt_toolkit import prompt, choice
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style as prompt_style
from prompt_toolkit.formatted_text import HTML

def choix1():
	style = prompt_style.from_dict(
    {
        "frame.border": "#F11BAA",
        "selected-option": "bold",
    }
	)
	i = choice(
				message=HTML("<u>Choississez une action :</u>"),
				options=[
					("idx_horo", "Entrer l'idx de la phrase neg à écouter"),
					("debut", "Écouter les phrases négatives à p. du début"),
					("q", "quitter")
				],
				default="q",
				style=style,
				show_frame=True
			)
	return i

def choix2():
	style = prompt_style.from_dict(
    {
        "frame.border": "#1BF130",
        "selected-option": "bold",
    }
	)
	i = choice(
		message=HTML("<u>Choississez une action :</u>"),
		options=[
			("r", "Répéter la phrase"),
			("m", "Modifier et/ou valider la phrase"),
			("e", "Pas de négation, écouter la phrase suivante"),
			("q", "Revenir au menu principal")
		],
		default="m",
		style=style,
		show_frame=True
	)
	return i

def modif_phrase(hms: str, phrase: str):
	""" Lance le prompt
		crée un binding pour les touches du clavier
		(optionnel mais peut être utile pour personnaliser l'édition)
	"""
	
	kb = KeyBindings()
	prompt_phrase = prompt(f"Modifier la phrase :  ", default=phrase, key_bindings=kb)	
	nouvelle_phrase = (hms, prompt_phrase)
	return nouvelle_phrase

def idx_horo_fichier(chemin_fichier: str):
	""" Retourne le idx_horo situé au début du nom de fichier qui servira de clé de tri"""
	return float(chemin_fichier.split('/')[-1].split('_')[0])


def read_audiofile(chemin_rep_transcript: str, chemin_rep_audio: str, nom_debat: str):
	"""
		Ouvre simultanément :
		- le fichier de la phrase négative transcrite et l'affiche sur le Terminal
		- le fichier du segment audio correspondant et le lit
		Ouvre un prompt permettant de modifier la phrase
		Return : la liste des phrases à entrer dans la colonne phrase corrigée du df, csv
	""" 
	
	list_transcripts = glob(chemin_rep_transcript + '/*.txt')
	list_transcripts.sort(key=idx_horo_fichier)
	

	list_audio = glob(chemin_rep_audio + '/*.mp3')
	list_audio.sort(key=idx_horo_fichier)
	
	format_idx_horo = re.compile(r'\d+\.\d{1,3}')

	list_ph_corr = []
	
	while True:
		try:
			i = choix1()
			if i == "idx_horo":
				i = input("entrez l'idx_horo : \n")
				if format_idx_horo.match(i):
					cpteur = 0
					for transcript, audio in zip(list_transcripts[list_transcripts.index(f"../output/ph_neg/{nom_debat}/{nom_debat}_txt/{str(i)}_{nom_debat}.txt")+cpteur:], 
									list_audio[list_audio.index(f"../output/ph_neg/{nom_debat}/{nom_debat}_audio/{str(i)}_{nom_debat}.mp3")+cpteur:]):
						print(idx_horo_fichier(transcript))
						with open(transcript) as f:
							print(f"Phrase négative idx_horo {idx_horo_fichier(transcript)} :\n")
							phrase = f.readline()
							print(phrase + "\n\n")
							if 'plus' in phrase:
								print(Back.YELLOW + "DÉSAMBIGUÏSATION de" + Fore.RED +' PLUS' + colorstyle.RESET_ALL)
							sound = AudioSegment.from_file(audio, format="mp3")
							no_break = True
							while no_break:
								play(sound)
								s = choix2()
								if s == "r":
									continue
								elif s == "m":
									list_ph_corr.append(modif_phrase(idx_horo_fichier(transcript), phrase))
									cpteur+=1
									break
								elif s == "e":
									list_ph_corr.append((idx_horo_fichier(transcript), 'N/A'))
									cpteur+=1
									break
								elif s == "q":
									no_break = False
							if no_break == False:
								break
							else:
								cpteur+=1
								continue
				else:
					print("le format de idx_horo n'est pas reconnu, veuillez recommencer.")
					continue
			elif i == "q":
						break
			elif i == "debut":
				cpteur = 0
				for transcript, audio in zip(list_transcripts, list_audio):
					with open(transcript) as f:
						cpteur += 1
						print(f"Phrase négative idx_horo : {idx_horo_fichier(transcript)} :\n")
						phrase = f.readline()
						print(phrase + "\n\n")
						if ' plus ' in phrase:
							print(Back.YELLOW + "DÉSAMBIGUÏSATION de" + Fore.RED +' PLUS' + colorstyle.RESET_ALL)
						sound = AudioSegment.from_file(audio, format="mp3")
						no_break = True
						while no_break:
							play(sound)
							s = choix2()
							if s == "r":
								continue
							elif s == "m":
								list_ph_corr.append(modif_phrase(idx_horo_fichier(transcript), phrase))
								break
							elif s == "e":
								list_ph_corr.append((idx_horo_fichier(transcript), 'N/A'))
								break
							elif s == "q":
								no_break = False
						if no_break == False:
							break
						else:
							continue
			else:
				continue
		except Exception as e:
			print(f"Error : {e}")
		 
	print(f"list_ph_corr : {list_ph_corr}\n")
	return list_ph_corr