from normalise_transcript import EN_spacy, concat_seg_horo
# from normalise_transcript import *
from utils import *

from pydub import AudioSegment
from pydub.playback import play

import os
import datetime
# from datastructure import Token, Sentence, Corpus
import spacy
import re
import csv
from collections import OrderedDict


def find_neg(transcripts_list: list[tuple[str]])-> dict[tuple,list[str]]:
	""" Détecte les phrases négatives à partir des occurrences de mots formes ou à p. d'une regex
		utlise Spacy pour désambiguïser les "plus" grâce étiquette Polarity=Neg
		Renvoie un dico avec clé : (horo, texte de la phrase), valeur : liste des formes négatives trouvées dans la phrase
	"""
	# global NEGATION
	global motif_neg
	modele = spacy.load("fr_dep_news_trf")
	dico_ph_neg = {}
	# dico_ph_neg = OrderedDict()
	for e in transcripts_list:
		if e[1] != "":
			heure, tokens = e[0], modele(e[1])
			# print(tokens)
			s = tokens.text # la str de la phrase
			m = motif_neg.findall(s)
			for t in tokens:
				if t.text == "plus" and "Polarity=Neg" not in t.morph:
					pass
				elif t.text in m:
					# print(t.text)
					if (heure, e[1]) in dico_ph_neg:
						dico_ph_neg[(heure, e[1])].append(t.text)
					else:
						dico_ph_neg[(heure, e[1])] = [t.text]					
			# for t in tokens:
			# 	# print(t)
			# 	# print(NEGATION)
			# 	if t.text == "plus" and "Polarity=Neg" not in t.morph:
			# 		pass
			# 	elif t.text in NEGATION:
			# 		if (heure, e[1]) in dico_ph_neg:
			# 			dico_ph_neg[(heure, e[1])].append(t.text)
			# 		else:
			# 			dico_ph_neg[(heure, e[1])] = [t.text]

	# ordonner le dico par clé
	print(f"nbre de phrases négatives: {len(dico_ph_neg)}")
	return dico_ph_neg

def stats_ph_neg(dico_ph_neg: dict)-> dict[str,int]:
	# global NEGATION
	# dico_formes_neg = {}
	# for k, v in dico_ph_neg.items():
	# 	for e in v:
	# 		if e in NEGATION:
	# 			if e in dico_formes_neg:
	# 				dico_formes_neg[e] += 1
	# 			else:
	# 				dico_formes_neg[e] = 1
	# 		else:
	# 			print(e)
	global motif_neg
	dico_formes_neg = {}
	for k, v in dico_ph_neg.items():
		motif_neg.findall()
		if e in NEGATION:
			if e in dico_formes_neg:
				dico_formes_neg[e] += 1
			else:
				dico_formes_neg[e] = 1
		else:
			print(e)
	print(dico_formes_neg)
	return


def make_csv(dico_ph_neg: dict[tuple[str]], nom_fichier_csv: str):
	with open(f'../output/csv/{nom_fichier_csv}', 'w') as file:
		writer = csv.writer(file, delimiter='\t')
		entetes = ['n°', 'heure', 'phrase neg', 'forme neg']
		writer.writerow(entetes)
		cpteur = 0
		for k, v in dico_ph_neg.items():
			cpteur += 1
			time_str = k[0]
			print(time_str)
			time_float = float(time_str[:time_str.index('-')-1])
			h = sec2hms(time_float)
			# print(h)
			# print(k[1])
			# print(v)
			data = [cpteur, h, k[1], v]
			writer.writerow(data)
	return

def horo_transcr_ph_neg(chemin_audio_file: str, dico_ph_neg: dict[tuple[str]], chemin_rep, nom_repertoire_cree: str):
	""" Convertit les horodateurs donnés au format sec au format millisecondes
		pour s'adapter à PyDub https://github.com/jiaaro/pydub/blob/master/README.markdown
		qui segmente fichier audio en plusieurs fichiers audios
		Retourne :
		- deux répertoires de fichiers parallèles : l'audio et la transcription des phrases négatives
		- double utilité : 
		* corriger chaque transcription avec écoute
		* garder les fichiers audio et les transcriptions phrases negatives corrigées pour entraîner Wave2Vec ou autre ASR
	"""
	# list_horos_neg = [(convert2millisec(e[0].split(':')), e[1]) for e in ph_neg] # e[1] est la transcription
	# print(type(list_horos_neg[0])) # class float

	print(dico_ph_neg)
	sound = AudioSegment.from_file(chemin_audio_file, "mp3")
	# play(sound)

	try:
		os.mkdir(f"{chemin_rep}{nom_repertoire_cree}")

		os.mkdir(f"{chemin_rep}{nom_repertoire_cree}/{nom_repertoire_cree}_audio")
		os.mkdir(f"{chemin_rep}{nom_repertoire_cree}/{nom_repertoire_cree}_txt")
    	# print(f"Directory '{nom_repertoire_cree}' created successfully.")
	except FileExistsError:
		print(f"Directory '{nom_repertoire_cree}' already exists.")
		pass
	
	cpteur = 0
	for k, v in list(dico_ph_neg.items()): # dico est-il ordonné par time ici ?
		cpteur += 1
		# start_ms = p[0] # start of clip in milliseconds
		# print(f"k : {k}, v : {v}")
		start_ms = float(k[0][:k[0].index('-')-1])*1000
		# end_ms = start_ms + 10000.0 #end of clip in milliseconds
		end_ms = float(k[0][k[0].index('-')+2:])*1000
		# print(start_ms, end_ms)
		splice = sound[start_ms:end_ms]
		splice.export(f"../output/{chemin_rep}{nom_repertoire_cree}/{nom_repertoire_cree}_audio/{cpteur}_{nom_repertoire_cree}.mp3", format="mp3")
		with open(f"../output/{chemin_rep}{nom_repertoire_cree}/{nom_repertoire_cree}_txt/{cpteur}_{nom_repertoire_cree}.txt", "w") as f_out:
			f_out.write(k[1])
	return





if __name__ == "__main__":
	
	NEGATION = ["n'", "N'", "ne", "Ne", "pas", "jamais", "plus", "aucun", "aucune", "aucuns", "aucunes", "personne", "rien", "nul", "nuls", "nulle", "nulles"]
	motif_neg = re.compile(r"[Aa]ucune?s?|[Pp]ersonne|[Rr]ien|[Nn]ulles?(?: part)?|[Nn]ullement|[Nn]uls?|[Nn]'|[Nn]e|[Pp]as|[Jj]amais|[Pp]lus")
	
	nom_rep = "../output/debat_entier/europeennes_europe1/"
	# nom_fichier = "europeennes_europe1.txt"
	nom_fichier = "europeennes_europe1.txt"
	nom_transcript_complete = "europeennes_europe1_texte_entier.txt"
	nom_modele = "fr_core_news_lg"
	
	# print("extraction des EN")
	# doc = spacy_load_doc(nom_rep, nom_transcript_complete, nom_modele)
	# en = EN_spacy(doc)

	# print("concaténation des segments de phrases")
	# transcripts_list = concat_seg_horo(nom_rep, nom_fichier)
	# print(transcripts_list)
	

	# startTime = datetime.datetime.now()

	# ph_neg = find_neg(transcripts_list)
	# print(ph_neg)
	# endTime = datetime.datetime.now()
	# print(f"Temps traitement extraction ph neg : {endTime - startTime}")

	# # stats_ph_neg(ph_neg)

	startTime = datetime.datetime.now()

	audiofile = '../audio/debat_entier/europeennes_europe1.mp3' # path to audiofile
	chemin_rep_ph_neg = "../output/ph_neg/"
	nom_rep_ph_neg = "europeennes_europe1"
	# horo_transcr_ph_neg(audiofile, ph_neg, chemin_rep_ph_neg, nom_rep_ph_neg)
	
	# endTime = datetime.datetime.now()
	# print(f"Temps traitement reps de ph neg et fichiers audios : {endTime - startTime}")

	# startTime = datetime.datetime.now()
	# make_csv(ph_neg, "europeennes_europe1.csv")
	# endTime = datetime.datetime.now()
	# print(f"Temps traitement make_csv() : {endTime - startTime}")

	chemin_transcript = f"../output/ph_neg/europeennes_europe1/{nom_rep_ph_neg}_txt/"
	chemin_audio = f"../output/ph_neg/europeennes_europe1/{nom_rep_ph_neg}_audio/"
	read_audio_files(chemin_transcript, chemin_audio)


