import re
import csv
import polars as pl
import spacy
import os
import sys
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utils'))
import manip_csv

""" Fonctions qui permettent d'ajouter dans une nouvelle colonne des données extraites d'une colonne dans le df.
	Autant de def() que de caractéristiques à extraire
	les fonctions
"""
def compte_global_mots_neg(chemin_fichier_csv_in: str, nom_fichier_csv_in: str):
	global list_mots_neg
	df = manip_csv.csv_to_df(chemin_fichier_csv_in,nom_fichier_csv_in)
	nveau_df = pl.DataFrame()
	for m in list_mots_neg:
		sum_df = df.select(
		pl.col("mot forme négation")
		.str.split(by=", ")
		.list.count_matches(m)
		.sum()
		.alias(f"compte : {m}"))
		print(int(sum_df))
		# pl.concat([nveau_df, sum_df])
	# pl.concat([nveau_df,somme_df])
		# df.join(df, on="phrase_corrigee", how="left")
		
	# manip_csv.print_df(nveau_df)
	return

def calcul_stats_gen(chemin_fichier_csv_in: str, nom_fichier_csv_in: str):
	# liste triée minuscules pour dico de comptage
	list_mots_neg = ['aucun', 'aucune', 'jamais', "n'", 'ne', 'ni', 'nul', 'nulle', 'nulle part', 'nullement', 'nulles', 'nuls', 'pas', 'personne', 'plus', 'rien']

	dico_formes_neg = {}
	for e in list_mots_neg:
		dico_formes_neg[e] = 0
	chemin_fichier_csv_out = "../output/csv/stats_gen/"
	nom_fichier_csv_out  = "occurrences_formes_neg.csv"
	with open(chemin_fichier_csv_in + nom_fichier_csv_in) as f:
		f.readline()
		lecture = csv.reader(f, delimiter=',')
		for r in lecture:
			m = motif_neg.findall(r[6])
		# Compte occurrences
			for t in m:
				t = t.strip().lower()
				if t in dico_formes_neg.keys():
					dico_formes_neg[t] += 1
				else:
					print(f"{t.lower()} n'est pas dans dico formes")
	# Insertion des occurrences calculées dans le csv stats_gen
	dic_list = list(dico_formes_neg.items())
	# dic_list.insert(0,('nom_debat', nom_debat))
	dico_formes_neg = dict(dic_list)
	# crée un df à p. du dico
	df = pl.DataFrame(dico_formes_neg)
	manip_csv.print_df(df)
	if os.path.exists(chemin_fichier_csv_out+nom_fichier_csv_out):
		with open(chemin_fichier_csv_out+nom_fichier_csv_out, 'a') as f_out:
			r = df.row(0)
			r = list(r)
			ecrire = csv.writer(f_out, delimiter=',')
			ecrire.writerow(r)
	else:	
		# on fait un csv avec les stats générales des formes négatives
		manip_csv.df_to_csv(chemin_fichier_csv_out, nom_fichier_csv_out, df)
	return

def add_feature_col_regex(chemin_fichier_csv: str, nom_fichier_csv: str, motif_re: str, nom_feat: str):
	""" Recherche de feat en passant par un df
		Prend un csv et une regex à appliquer à la col 'phrase corrigée', applique la regex à chaque rang 
		et ajoute le résultat dans une une col supp.
	"""
	df = manip_csv.csv_to_df(chemin_fichier_csv,nom_fichier_csv)
	# manip_csv.print_df(df)
	# nveau_df = df.with_columns(pl.col("phrase_corrigee").str.contains(r"\b([Nn]'|[Nn]e)\b").alias(nom_feat))
	nveau_df = df.with_columns(pl.col("phrase_corrigee").str.extract_all(motif_re).list.join(", ").alias(nom_feat))
	# nveau_df = nveau_df.select(pl.col(nom_feat).list.join(", "))
	manip_csv.print_df(nveau_df)
	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplace le précédent
	# manip_csv.df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return
def forme_neg(texte: str):
	tokens = nlp(texte)
	s = tokens.text
	m = motif_neg.findall(s)
	return ", ".join([token.text for token in tokens if token.text in m])

def tete_neg(texte: str):
	tokens = nlp(texte)
	s = tokens.text
	m = motif_neg.findall(s)
	return ", ".join([token.head.text for token in tokens if token.text in m])

def pos_tete_neg(texte: str):
	tokens = nlp(texte)
	s = tokens.text
	m = motif_neg.findall(s)
	return ", ".join([token.head.pos_ for token in tokens if token.text in m])

def longueur_phrase(texte: str):
	tokens = nlp(texte)
	return len([t for t in tokens])

def posi_neg(texte: str):
	tokens = nlp(texte)
	s = tokens.text
	m = motif_neg.findall(s)
	#TODO
	return 

def add_feature_col_spacy(chemin_fichier_csv: str, nom_fichier_csv: str, nom_model_spacy: str):
	""" Recherche de feat en passant par un df
		Prend un csv et un modèle spacy à appliquer à la col 'phrase corrigée',  à chaque rang 
		et ajoute le résultat dans une une col supp.
	"""
	global motif_neg
	global list_verb_modaux

	nlp = spacy.load(nom_model_spacy)
	# tokens = [nlp(p) for p in df["phrase_corrigee"]] # liste chque ph_neg est un doc spacy(44 sec)
	df = manip_csv.csv_to_df(chemin_fichier_csv,nom_fichier_csv)
	#___________________________________________ SPACY_________________________________________________________
	
	
	# s = pl.Series(tokens) # itérable
	# nveau_df = df.with_colums()
	
	#___________________________________________ REGEX EXTRACT _________________________________________________________
	# hiatus voyelles

	# geminisation
	# nveau_df = df.filter(pl.col("phrase_corrigee").str.contains(r"\b[O|o]n\b [aeiouy]\p{L}* pas").alias("geminisation"))

	#cluster consonnes le pas ne doit pas être précédé de 'ou' ou 'et'
	# nveau_df = df.filter(pl.col("phrase_corrigee").str.contains(r"\b\p{L}+[bcdfgjklmnpqrtvwxz]\b [aeiouy]\p{L}*(?<!\bou\b|\bet\b) pas")).select(pl.col("n_ph","phrase_corrigee"))
	nveau_df = df.with_columns(pl.col("phrase_corrigee").str.contains(r"\b\p{L}+[bcdfgjklmnpqrtvwxz]\b [aeiouy]\p{L}*(?!\bou\b|\bet\b) pas")).select(pl.col("n_ph","phrase_corrigee"))

	# nveau_df = nveau_df.with_columns(pl.col("phrase_corrigee").str.split(by=" ").list.count_matches("je").alias("pronom_je"))
	# nveau_df = df.filter(pl.col("phrase_corrigee").str.contains(r"\b.+[bcdfgjklmnpqrtvwxz]\b \b[aeiouy].+\b pas"))

	# nveau_df = df.with_columns(
	# 	(pl.col("phrase_corrigee")
	# 	.str.extract_all(motif_neg)
	# 	.alias("mots forme négation")
   	# 	.list.contains(r"n'|ne")
	# 	.alias("pres 'ne'")),
	# 	(pl.col("phrase_corrigee")
   	# 	.str.split(by=" ")
	# 	.list.len()
	# 	.alias("longueur phrase"))
	# 	)
	
	# nveau_df = df.with_columns(pl.col("mot forme négation").str.split(by=", ").list.contains("pas").alias("pres 'ne'"))

	
	# nveau_df = df.with_columns(pl.col("phrase_corrigee").list.eval(pl.element().longueur_phrase()).alias("longueur phrase"))
	
	
	manip_csv.print_df(nveau_df)
	# manip_csv.df_to_csv(chemin_fichier_csv, nom_fichier_csv, nveau_df)
	return

def formes_neg_traitement(chemin_fichier_csv_in: str, nom_fichier_csv_in: str, nom_model_spacy: str):
	""" recherche de feats dans le csv en lisant la colonne 'phrase corrigée de chaque rang """
	# global options_affichage
	global motif_neg
	nlp = spacy.load(nom_model_spacy)

	list_forme_neg = []
	list_tete_neg = []
	list_pos_tete = []
	list_bool_ne = []
	
	with open(chemin_fichier_csv_in+nom_fichier_csv_in) as f:
		f.readline()
		lecture = csv.reader(f, delimiter=',')
	
		for r in lecture:
			# Recherche des features : mot polarisé (polarity=Neg), tête du mot polarisé, pos de la tête, présence ou abscence de 'ne'
			tokens = nlp(r[6])
			s = tokens.text
			m = motif_neg.findall(s)
			# list_forme = [token.text for token in tokens if "Polarity=Neg" in token.morph]
			list_forme = [token.text for token in tokens if token.text in m]
			# list_tete = [token.head.text for token in tokens if "Polarity=Neg" in token.morph]
			list_tete = [token.head.text for token in tokens if token.text in m]
			# list_tete_pos = [token.head.pos_ for token in tokens if "Polarity=Neg" in token.morph]
			list_tete_pos = [token.head.pos_ for token in tokens if token.text in m]
			list_bool_ne.append([1 if token.text.lower() in ("n'","ne") else 0 for token in tokens])
			list_forme_neg.append(list_forme)
			list_tete_neg.append(list_tete)
			list_pos_tete.append(list_tete_pos)


	list_forme_neg = [', '.join(list(set(e))) if e != [] else "N/A" for e in list_forme_neg]
	list_tete_neg = [', '.join(list(set(e))) if e != [] else "N/A" for e in list_tete_neg]
	list_pos_tete = [', '.join(list(set(e))) if e != [] else "N/A" for e in list_pos_tete]
	list_bool_ne = [1 if 1 in e else 0 for e in list_bool_ne]

	assert len(list_forme_neg) == len(list_tete_neg) == len(list_pos_tete) == len(list_bool_ne)

	# Ajout des colonnes en passant par un df (visu)
	manip_csv.add_col_to_csv(chemin_fichier_csv_in, nom_fichier_csv_in, list_forme_neg, "mot forme négation")
	manip_csv.add_col_to_csv(chemin_fichier_csv_in, nom_fichier_csv_in, list_tete_neg, "tête négation")
	manip_csv.add_col_to_csv(chemin_fichier_csv_in, nom_fichier_csv_in, list_pos_tete, "POS tête négation")
	manip_csv.add_col_to_csv(chemin_fichier_csv_in, nom_fichier_csv_in, list_bool_ne, "'ne' prés")

	return

if __name__ == "__main__":
	
	motif_neg = r"\b([Aa]ucune?s?|[Pp]ersonne|[Rr]ien|[Nn]ulles?(?: part)?|[Nn]ullement|[Nn]uls?|[Nn]'|[Nn]e|[Pp]as|[Jj]amais|[Pp]lus|[Nn]i)\b"
	# motif_neg_comp = re.compile(r"\b([Aa]ucune?s?|[Pp]ersonne|[Rr]ien|[Nn]ulles?(?: part)?|[Nn]ullement|[Nn]uls?|[Nn]'|[Nn]e|[Pp]as|[Jj]amais|[Pp]lus|[Nn]i)\b")
	list_mots_neg = ['aucun', 'aucune', 'jamais', "n'", 'ne', 'ni', 'nul', 'nulle', 'nulle part', 'nullement', 'nulles', 'nuls', 'pas', 'personne', 'plus', 'rien']
	list_verb_modaux = ["falloir", "pouvoir", "devoir", "penser", "croire", "savoir", "permettre", "vouloir"]
	chemin_fichier_csv = "../output/csv/annotations_csv/"
	# nom_fichier = nom_debat+'.csv'
	nom_fichier_csv_final = "ph_neg_debats.csv"
	
	# chemin_envois_csv = "../envois/csv/"
	# nom_fichier_csv_envoye = nom_debat + '_formes_neg.csv'
	# del_col(chemin_fichier_csv, nom_debat+'.csv',"formes_neg")
	#
	# list_cols_a_envoyer = ["n_ph", "hms", "phrase_corrigee", "formes_neg"]
	# manip_csv.select_cols_to_csv(chemin_fichier_csv, nom_debat+'.csv', list_cols_a_envoyer, chemin_envois_csv, nom_fichier_csv_envoye)
	nom_modele = "fr_dep_news_trf"
	# startTime = datetime.datetime.now()
	# formes_neg_traitement(chemin_fichier_csv, nom_fichier_csv_final, nom_modele)

	# add_feature_col_regex(chemin_fichier_csv, nom_fichier_csv_final, motif_neg, "mot forme négation")
	# endTime = datetime.datetime.now()
	# print(f"Temps traitement : {endTime - startTime}")
	startTime = datetime.datetime.now()
	add_feature_col_spacy(chemin_fichier_csv, nom_fichier_csv_final, nom_modele)
	# compte_global_mots_neg(chemin_fichier_csv, nom_fichier_csv_final)
	endTime = datetime.datetime.now()
	print(f"Temps traitement : {endTime - startTime}")
