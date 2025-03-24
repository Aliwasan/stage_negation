import argparse
import datetime
import os
import sys
import spacy
import re
import polars as pl
import json
rep_courant = os.path.dirname(__file__)
print(rep_courant)
sys.path.append(os.path.join(rep_courant, '..', 'Utils')) # __file__ : chemin absolu du script courant               
import utils, manip_csv
from pydub import AudioSegment
from normalise_transcript import concat_seg_horo


def find_neg(transcripts_list: list[tuple[str]])-> dict[tuple,list[str]]:
	""" Détecte les phrases négatives à partir à p. d'une regex des mots négatifs
		utilise Spacy pour désambiguïser les "plus" grâce étiquette Polarity=Neg
		Renvoie un json avec 
	"""
	global motif_neg
	modele = spacy.load("fr_dep_news_trf")
	data_ph_neg = []
	n_ph = 1
	for e in transcripts_list:
		ph_neg = {}
		if e[1] != "":
			tokens = modele(e[1]) # l'objet phrase spacy doc
			s = tokens.text # la str de la phrase
			m = motif_neg.findall(s)
			for i,t in enumerate(tokens):
				if t.text in m:
					# tests de désambiguïsation de plus et pas car on veut l'expression "c'est pas"
					if t.text == "plus" and "Polarity=Neg" not in t.morph:
						continue # on prend le token suivant
					elif t.text == "pas" and "Polarity=Neg" not in t.morph:
						# test si le "pas" suit un "c'est" on part du pppe que seuls des ADV en ment sont placés entre est et pas.
						if tokens[i-2:i].text.lower() == "c'est"\
							or tokens[i-3:i].text.lower() == "ce n'est"\
							or (tokens[i-3:i-1].text.lower() == "c'est" and "ADV" in [t.pos_ for t in tokens[i-3:i]])\
							or (tokens[i-4:i-1].text.lower() == "ce n'est" and "ADV" in [t.pos_ for t in tokens[i-4:i]]):
							ph_neg['n_ph'] = n_ph
							ph_neg['horo'] = e[0] # ex : "582.56 - 583.68"
							ph_neg['hms'] = utils.sec2hms(e[0]) # ex : 00:09:42
							ph_neg['sent'] = e[1]
							data_ph_neg.append(ph_neg)
							n_ph += 1
							break # suffit à prendre la ph on peut sortir de la boucle tokens
						else:
							continue # on prend le token suivant
					else:
						# print(t.text)
						ph_neg['n_ph'] = n_ph
						ph_neg['horo'] = e[0] # ex : "582.56 - 583.68"
						ph_neg['hms'] = utils.sec2hms(e[0]) # ex : 00:09:42
						ph_neg['sent'] = e[1]
						# ph_neg['formes_neg'].append([t.text])
						data_ph_neg.append(ph_neg)
						n_ph += 1
						break # suffit à prendre la ph on peut sortir de la boucle tokens
				else:
					pass
	print(f"nbre de phrases négatives: {len(data_ph_neg)}")
	with open(f'../output/json/{nom_debat}.json', 'w') as output_json:
		json.dump(data_ph_neg, output_json, indent=4)
	df = pl.DataFrame(data_ph_neg)
	# print(df)
	return df

def horo_transcr_ph_neg(chemin_audio_file: str, chemin_json_ph_neg: str, nom_debat: str, chemin_rep_output_audio: str):
	""" permet de corriger chaque transcription avec écoute.
		Convertit les horodateurs donnés au format sec au format millisecondes
		pour s'adapter à PyDub https://github.com/jiaaro/pydub/blob/master/README.markdown
		qui segmente fichier audio en plusieurs fichiers audios
		Retourne :
		- deux répertoires de fichiers parallèles : l'audio et la transcription des phrases négatives
	"""

	sound = AudioSegment.from_file(chemin_audio_file, "mp3")

	try:
		os.mkdir(f"{chemin_rep_output_audio}{nom_debat}")
	except FileExistsError:
		print(f"Directory : {chemin_rep_output_audio}{nom_debat} already exists.")
	try:
		os.mkdir(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_audio")
	except FileExistsError:
		print(f"Directory : {chemin_rep_output_audio}{nom_debat}/{nom_debat}_audio already exists.")
	try:
		os.mkdir(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_txt")
	except FileExistsError:
		print(f"Directory : {chemin_rep_output_audio}{nom_debat}/{nom_debat}_txt already exists.")
	
	cpteur = 0
	with open(chemin_json_ph_neg + nom_debat + '.json', 'r') as json_file_in:
		data = json.load(json_file_in)
		# print(type(data))
		for e in data:
			if e != {}:
				start_ms = (float(e['horo'][:e['horo'].index('-')-1])*1000)-1000.0
				end_ms = (float(e['horo'][e['horo'].index('-')+2:])*1000)+1000.0
				# print(start_ms, " - " , end_ms)
			cpteur += 1
			splice = sound[start_ms:end_ms]
			splice.export(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_audio/{cpteur}_{nom_debat}.mp3", format="mp3")
			with open(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_txt/{cpteur}_{nom_debat}.txt", "w") as f_out:
				f_out.write(e['sent'])
	return


if __name__ == "__main__":
	
	motif_neg = re.compile(r"[Aa]ucune?s?|[Pp]ersonne|[Rr]ien|[Nn]ulles?(?: part)?|[Nn]ullement|[Nn]uls?|[Nn]'|[Nn]e|[Pp]as|[Jj]amais|[Pp]lus|[Nn]i")
	
	parser = argparse.ArgumentParser(description="1er argument : nom du débat")
	parser.add_argument("nom_debat", help="nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	nom_rep = "../output/debat_entier/" + nom_debat +"/"
	nom_fichier = nom_debat + ".txt"
	nom_transcript_complete = nom_debat + "_texte_entier.txt"

	# print("concaténation des segments de phrases")
	# transcripts_list = concat_seg_horo(nom_rep, nom_fichier)
	# print(transcripts_list)
	# print(f"len(transcript_list) : {len(transcripts_list)}")
	
	# startTime = datetime.datetime.now()
	# df_json_ph_neg = find_neg(transcripts_list)

	# chemin_fichier_csv = "../output/csv/"
	# nom_fichier_csv = nom_debat + ".csv"

	# manip_csv.df_to_csv(chemin_fichier_csv, nom_fichier_csv, df_json_ph_neg)
	# endTime = datetime.datetime.now()
	# print(f"Temps traitement extraction ph neg : {endTime - startTime}")

	startTime = datetime.datetime.now()
	audiofile = "../audio/debat_entier/" + nom_debat + ".mp3" # path to audiofile
	chemin_rep_ph_neg = "../output/json/"
	chemin_rep_output_audio = "../output/ph_neg/"
	
	horo_transcr_ph_neg(audiofile, chemin_rep_ph_neg, nom_debat, chemin_rep_output_audio)
	endTime = datetime.datetime.now()
	print(f"Temps traitement fichiers audios : {endTime - startTime}")