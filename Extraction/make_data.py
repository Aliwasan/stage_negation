import argparse
import datetime
import os
import sys
import spacy
import re
import polars as pl
import json
import glob

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utils'))        
import utils, manip_csv, desamb_spacy
from pydub import AudioSegment
from normalise_transcript import concat_seg_horo


def find_neg(transcripts_list: list[tuple[str]], nom_modele: str)-> dict[tuple,list[str]]:
	""" 
		Détecte les phrases négatives à partir à p. d'une regex des mots négatifs
		utilise un modèle de langue Spacy pour désambiguïser les "pas", "plus", "personne" grâce étiquette Polarity=Neg
		Renvoie un json avec pour chaque phrase négative : 
		le nom du débat, indice de phrase, bornes temporelles en sec et en hms, la phrase négative
	"""
	global motif_neg
	modele = spacy.load(nom_modele)
	data_ph_neg = []
	n_ph = 1
	
	for e in transcripts_list:
		ph_neg = {}
		if e[1] != "":
			tokens = modele(e[1])
			m1 = motif_neg.findall(e[1])
			if ('VERB' not in [tok.pos_ for tok in tokens]) and ('AUX' not in [tok.pos_ for tok in tokens]):
				continue
			elif len([tok.pos_ for tok in tokens if tok.pos_ != 'PUNCT']) <= 2:
				continue
			else:
				for t in tokens:
					if t.text in m1:
						if "Polarity=Neg" in t.morph:
							if desamb_spacy.pas_plus_deb_ph(tokens, t):
								continue
							elif desamb_spacy.precede_pas(tokens, t):
								continue
							elif desamb_spacy.inf_precede_negateur(tokens, t, 'pas', 7):
								continue
							else:
								ph_neg['nom_debat'] = nom_debat
								ph_neg['n_ph'] = n_ph
								ph_neg['horo'] = e[0]
								h_deb = e[0].split(' - ')[0]
								ph_neg['idx_horo'] = h_deb[:h_deb.index('.')+4]
								ph_neg['hms'] = utils.sec2hms(e[0])
								ph_neg['sent'] = e[1]
								data_ph_neg.append(ph_neg)
								n_ph += 1
								break
						else:
							if desamb_spacy.desambiguisation(tokens, t):
								continue
							else:
								ph_neg['nom_debat'] = nom_debat
								ph_neg['n_ph'] = n_ph
								ph_neg['horo'] = e[0]
								h_deb = e[0].split(' - ')[0]
								ph_neg['idx_horo'] = h_deb[:h_deb.index('.')+4]
								ph_neg['hms'] = utils.sec2hms(e[0])
								ph_neg['sent'] = e[1]
								data_ph_neg.append(ph_neg)
								n_ph += 1
								break
					else:
						pass

	with open(f'../output/json/{nom_debat}.json', 'w') as output_json:
		json.dump(data_ph_neg, output_json, indent=4)
	df = pl.DataFrame(data_ph_neg)
	manip_csv.print_df(df)
	return df

def horo_transcr_ph_neg(chemin_audio_file: str, chemin_json_ph_neg: str, nom_debat: str, chemin_rep_output_audio: str):
	""" permet de corriger chaque transcription avec écoute.
		Convertit les horodateurs donnés au format sec en millisecondes
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
		for e in data:
			if e != {}:
				start_ms = (float(e['horo'][:e['horo'].index('-')-1])*1000)-1000.0
				end_ms = (float(e['horo'][e['horo'].index('-')+2:])*1000)+1000.0
			cpteur += 1
			splice = sound[start_ms:end_ms]
			splice.export(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_audio/{e['idx_horo']}_{nom_debat}.mp3", format="mp3")
			with open(f"{chemin_rep_output_audio}{nom_debat}/{nom_debat}_txt/{e['idx_horo']}_{nom_debat}.txt", "w") as f_out:
				f_out.write(e['sent'])
	return


if __name__ == "__main__":
	
	motif_neg = re.compile(r"\b([Aa]ucune?s?|[Pp]ersonne|[Rr]ien|[Nn]ulles?(?: part)?|[Nn]ullement|[Nn]uls?|[Nn]'|[Nn]e|[Pp]as|[Jj]amais|[Pp]lus|[Nn]i)\b")

	parser = argparse.ArgumentParser(description="1er argument : nom du débat")
	parser.add_argument("nom_debat", help="nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	nom_rep = "../output/debat_entier/" + nom_debat +"/"
	nom_fichier = nom_debat + ".txt"
	nom_modele = "fr_dep_news_trf"
	print("concaténation des segments de phrases")
	transcripts_list = concat_seg_horo(nom_rep, nom_fichier)
	print(f"len(transcript_list) : {len(transcripts_list)}")
	chemin_fichier_csv = "../output/csv/"
	startTime = datetime.datetime.now()
	df_json_ph_neg = find_neg(transcripts_list, nom_modele)

	chemin_fichier_csv = "../output/csv/"
	nom_fichier_csv = nom_debat + ".csv"

	manip_csv.df_to_csv(chemin_fichier_csv, nom_fichier_csv, df_json_ph_neg)
	endTime = datetime.datetime.now()
	print(f"Temps traitement extraction ph neg : {endTime - startTime}")

	startTime = datetime.datetime.now()
	audiofile = "../audio/debat_entier/" + nom_debat + ".mp3"
	chemin_rep_ph_neg = "../output/json/"
	chemin_rep_output_audio = "../output/ph_neg/"
	
	horo_transcr_ph_neg(audiofile, chemin_rep_ph_neg, nom_debat, chemin_rep_output_audio)
	endTime = datetime.datetime.now()
	print(f"Temps traitement fichiers audios : {endTime - startTime}")