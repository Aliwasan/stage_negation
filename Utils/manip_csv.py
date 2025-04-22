import argparse
import polars as pl # type: ignore
import csv
import json
from typing import Union
import glob
import os.path
from collections import Counter
from pprint import pprint

def df_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, df):
	""" Prend un df et en fait un csv """
	df.write_csv(chemin_fichier_csv+nom_fichier_csv, include_header=True, null_value="N/A")
	return

def print_df(df):
	with pl.Config(tbl_rows=-1, tbl_cols=-1):
		return print(df)

def csv_to_df(chemin_fichier_csv: str, nom_fichier_csv: str):
	""" Prend un csv en fait un df """
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv,truncate_ragged_lines=True) #schema={'n_ph': i64,'horo': str,'hms': str,'sent': str,'phrase_corrigee': str}
	# print_df(df)
	return df

def list_de_list_to_df(entetes: list, liste: list[list]):
	""" Crée un df à p. d'une liste de liste où chque liste est un rang et une liste d'entêtes."""
	assert len(entetes) == len(liste[0])
	df = pl.DataFrame(liste, schema=entetes, strict=False)
	# print_df(df)
	return df

def tri_df(nom_col_tri: str, df):
	df = df.sort(nom_col_tri)
	# print_df(df)
	return df

def compare_df_col(chemin_fichier_csv1: str, fichier_csv_1: csv, chemin_fichier_csv2: str, fichier_csv_2: csv, nom_col: str):
	""" """
	df1 = csv_to_df(chemin_fichier_csv1, fichier_csv_1)
	df2 = csv_to_df(chemin_fichier_csv2, fichier_csv_2)
	col1 = set(df1[nom_col].to_list())
	col2 = set(df2[nom_col].to_list())
	print(col1.difference(col2))
	return

def json_to_csv(chemin_fichier_csv: str, chemin_fichier_json: str, nom_debat: str):
	# TODO
	return

def reindex_liste(list_a_reindexer: list[tuple], ecart: int):
	""" Incrémente ou décrémente en fonction de l'écart pos ou neg les index en position tuple[0] d'une liste de tuples"""
	for i,e in enumerate(list_a_reindexer):
		e = list(e)
		nvel_indx = e[0]
		if ecart > 0:
			nvel_indx += ecart
			e[0]=nvel_indx
			print(nvel_indx)
			e = tuple(e)
			print(e)
			list_a_reindexer[i]=e
			return list_a_reindexer
		elif ecart < 0:
			nvel_indx -= ecart
			e[0]=nvel_indx
			print(nvel_indx)
			e = tuple(e)
			print(e)
			list_a_reindexer[i]=e
			return list_a_reindexer

def check_csv_cols_nber(chemin_fichier_csv: str, nom_fichier_csv: str):
	with open(chemin_fichier_csv+nom_fichier_csv, newline='', encoding='utf-8') as f:
		reader = csv.reader(f)
		for row in reader:
			print(row[4])
			# if ', ' in row[4]:
			# 	print(row) 
	return

def csv_to_json(chemin_fichier_csv: str, nom_fichier_csv: str, chemin_fichier_json: str, nom_debat: str):
	""" on est parfois amené à faire un json à p. d'un csv pour refaire l'horo_transcr_ph_neg()
		après une insertion/modification
		pour mettre à jour les fichiers audio et txt
	"""	
	list_ph_neg = []
	with open(chemin_fichier_csv+nom_fichier_csv, 'r') as f:
		lecture = csv.reader(f, delimiter=',')
		list_ph_neg = [p for p in lecture]
	
	list_entetes = list_ph_neg[0]
	list_ph_neg.pop(0)
	print(list_ph_neg)
	# on fait un json
	data_list = []
	for item in list_ph_neg:
		json_dic = {}
		json_dic[list_entetes[0]] = item[0]
		json_dic[list_entetes[1]] = item[1]
		json_dic[list_entetes[2]] = item[2]
		json_dic[list_entetes[3]] = item[3]
		data_list.append(json_dic)

	with open(chemin_fichier_json+nom_debat+'.json', 'w') as output_json:
		json.dump(data_list, output_json, indent=4)
	return

def extract_col_csv(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col: str):
	""" Prend un csv en extrait au format liste la colonne dont le nom est donné en arg"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	print_df(df)
	to_update_column = df[nom_col].to_list()
	return df, to_update_column

def decale_rang_col_csv(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col: str, nb_rang_decal: int, start_index=None):
	""" Prend un csv en extrait la colonne dont le nom est donné en arg
		la réinsère à p. d'un rang plus bas dont l'index est donné en arg
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	col = df[nom_col].to_list()
	len_col = len(col) # 489
	print(f"len_col : {len_col}")
	a_deplacer = col[start_index-1:-nb_rang_decal] # ici on retire la dernière valeur N/A pour avoir un len() à la taille du df
	# on veut une ligne avec autant de N/A au début de la liste à insérer que de rangs avant les valeurs à insérer
	for _ in range(0,nb_rang_decal):
		a_deplacer.insert(0, "N/A") # ici on aura un rang avec N/A avant l'insertion
	print(f"a_deplacer : {a_deplacer}")
	print(f"len(a_deplacer) : {len(a_deplacer)})")
	# col_list = col.to_list()
	# on remet start_index pour que l'insertion parte bien de start_index sinon doublon ['a', 'b', 'b', 'c']
	col[start_index-1:start_index+len(a_deplacer)] = a_deplacer
	print(f"col : {col}")
	print(f"len(col) : {len(col)}")
	assert len_col == len(col)
	df = df.with_columns(pl.Series('phrase_corrigee', col))
	print_df(df)
	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplacera le précédent le cas échéant
	# df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return df

def add_col_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_ph: list, nom_col: str, idx_insert_col=None):
	""" 
		Insère une liste de données dans fichier csv préexistant
		à la suite des cols ou à un index de col donné
	"""

	df = pl.read_csv(chemin_fichier_csv + nom_fichier_csv)

	print(f"Taille du DataFrame: {df.height}")
	print(f"Taille de la liste des phrases: {len(list_ph)}")
	
	# Si list_ph est plus courte que le DataFrame, on la complète avec des valeurs None
	if len(list_ph) < df.height:
		list_ph.extend([None] * (df.height - len(list_ph)))
	s = pl.Series(nom_col, list_ph, strict=False)
	if idx_insert_col != None:
		df.insert_column(idx_insert_col, s)
	else:
		df = df.with_columns(s) # on insère la col à la suite des cols existantes
	print_df(df)
	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplacera le précédent le cas échéant
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return df

def add_in_col_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_ph: list, nom_col: str, start_row_idx=None, idx_insert_col=None):
	"""
		Insère une liste de données dans une colonne spécifique à partir d'un index de rang donné: 
		(par ex. suite de la correction des phrases d'un débat.)
	"""

	df = pl.read_csv(chemin_fichier_csv + nom_fichier_csv)

	print(f"Taille du DataFrame: {df.height}")
	print(f"Taille de la liste des phrases: {len(list_ph)}")
	
	# Vérifier si la colonne cible existe
	if nom_col not in df.columns:
		raise ValueError(f"La colonne {nom_col} n'existe pas dans le DataFrame.")		
	# Vérifier que la longueur des nouvelles données est compatible avec l'index de départ
	if start_row_idx >= df.height:
		raise ValueError("L'index de départ est supérieur ou égal au nbre de rangs du DataFrame.")
	
	# création de la Series avec les données à insérer
	s = pl.Series(nom_col, list_ph, strict=False)

	# Modifier la colonne existante à partir du rang donné
	to_update_column = df[nom_col].to_list()
	# print(to_update_column)

	# Insérer les nouvelles données à partir du rang spécifié
	# il faut décrémenter de 1 pour avoir la position exacte de l'insertion dans la liste
	start_row_idx -= 1
	print(f"start_row_idx dans la liste de la col :{start_row_idx}")
	to_update_column[start_row_idx:start_row_idx + len(list_ph)] = list_ph

	assert len(to_update_column) == df.height
	
	if idx_insert_col != None:
		df = df.insert_column(idx_insert_col, pl.Series(nom_col, to_update_column)) # on insère la col à la suite des cols existantes
	else:
		df = df.with_columns(pl.Series(nom_col, to_update_column))
	
	print(f"df après ajout de {nom_col} dans l'existant :\n {print_df(df)}")
	return df

def insert_row_in_df(chemin_fichier_csv: str, nom_fichier_csv: str, nom_cols: list[str], list_to_insert: list, insert_index=None ):
	""" Insère un ou plusieurs rangs à un csv sur ttes les cols
		en tenant compte de l'indexation préexistante
		l'index d'insertion est le n° de la phrase (n_ph démarre à 1)
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	
	# Ajout d'une valeur nulle pour la col "ph_corrigee"
	list_to_insert.append("N/A")
	
	if insert_index >= df.height:
		raise ValueError("L'index de départ est supérieur à la hauteur du DataFrame.")
	# vérification que la serie ait le même nbre de cols sur le rang d'avant l'insertion
	if len(list_to_insert) != len(df.row(insert_index-1)):
		raise ValueError("Le nombre de valeurs à insérer est différent au nbre de cols du DataFrame.")
	
	dic_to_insert = {}
	for a, b in zip(nom_cols, list_to_insert):
		dic_to_insert[a] = b

	# création d'un df avec les données à insérer
	df_to_insert = pl.DataFrame(dic_to_insert)
	
	# Pour insérer on est obligé de scinder puis de concaténer
	df_before = df.slice(0, insert_index)  # Rangs avant l'index d'insertion
	df_after = df.slice(insert_index, df.height - insert_index)  # Rangs après l'index d'insertion

	# reindexation des n_ph du bloc scindé après l'insertion
	list_index = df_after["n_ph"].to_list()
	list_index = [i+1 for i in list_index]
	# print(list_index)
	series_index = pl.Series("n_ph", list_index)
	df_after.replace_column(0, series_index)

	# Concatenation des 3 parties
	nveau_df = pl.concat([df_before, df_to_insert, df_after])
	print_df(df)
	# nveau_df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return df

def insert_data_in_df_col(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col_insertion: str, list_to_insert: list, insert_index=None ):
	""" insère un ou plusieurs rangs de données au format liste à une col. à partir d'un index donné
		S'il s'agit d'une insertion entre deux index de rangs de données, faire attention à la longueur de la liste et aux index pour ne pas écraser de données
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	list_to_insert = [p[1] for p in list_to_insert]
	if insert_index >= df.height:
		raise ValueError("L'index de départ est supérieur à la hauteur du DataFrame.")
	to_update_column = df[nom_col_insertion].to_list()
	insert_index -= 1
	print(f"start_index dans la liste de la col :{insert_index}")
	
	# Affectation de la liste comme valeur dans la col aux index prévus start_index jusqu'à la longueur de la liste à insérer
	# vérification de l partie de la col ou on va insérer
	print(to_update_column[insert_index:insert_index + len(list_to_insert)])
	to_update_column[insert_index:insert_index + len(list_to_insert)] = list_to_insert
	# print(f"len de la nouvelle colonne :{len(to_update_column)}")
	# print(to_update_column)
	print(len(to_update_column))
	df = df.with_columns(pl.Series('phrase_corrigee', to_update_column))
	print_df(df)
	# df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return df

def delete_row(chemin_fichier_csv: str, nom_fichier_csv: str, delete_index=None):
	""" efface un rang d'un csv et réindexe les rangs suivant le rang effacé 
		Donner le n° de rang du csv (les n° commençent à 1) 
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	# Pour réindexer on est obligé de scinder puis de concaténer
	df_before = df.slice(0, delete_index-1)  # Rows before insert index
	df_after = df.slice(delete_index, df.height - delete_index)  # Rows after insert index
	print(df_before)
	print(df_after)

	# reindexation des n_ph du bloc scindé après l'insertion
	list_index = df_after["n_ph"].to_list()
	list_index = [i-1 for i in list_index]
	# print(list_index)
	series_index = pl.Series("n_ph", list_index)
	df_after.replace_column(0, series_index)

	# Concatène avant et après
	nveau_df = pl.concat([df_before, df_after])
	print_df(nveau_df)
	nveau_df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return nveau_df

def del_col(chemin_fichier_csv: str, nom_fichier_csv: str, col_name: str, start_index=None):
	""" Ouvre un csv, supprime une col, écrit le nouveau csv, retourne le df """
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	if start_index != None:
		df = df.drop(col_name[start_index:])
	else:	
		df = df.drop(col_name)
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return df

def select_df_cols_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_noms_cols: list[str], \
					   chemin_nveau_fichier_csv: str, nom_nveau_fichier_csv: str):
	
	""" Sélectionne des cols d'un csv pour faire un nouveau csv avec """
	df = csv_to_df(chemin_fichier_csv, nom_fichier_csv)
	df_selected_cols = df.select(list_noms_cols)
	print_df(df_selected_cols)
	df_to_csv(chemin_nveau_fichier_csv, nom_nveau_fichier_csv, df_selected_cols)
	return df

def add_single_val_col_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, single_value: Union[str, int], nom_col: str, idx_insert_col=None):
	""" Insère une colonne avec une valeur unique à un fichier csv préexistant. """
	df = pl.read_csv(chemin_fichier_csv + nom_fichier_csv)
	df = df.insert_column(idx_insert_col, pl.lit(single_value).alias(nom_col))
	print(f"df nouveau débat :\n {print_df(df)}")
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return df

def concat_csv(liste_chemin_fichiers_csv: list[str]):
	""" prend une liste de chemin de fichiers csv (ex. glob.glob) """
	df = pl.concat([pl.read_csv(f) for f in liste_chemin_fichiers_csv]).with_row_index("idx_ph", offset=1)
	print_df(df)
	return df

def compare_2_csv_cols(liste_chemin_fichiers_csv: list[str]):
	for f in liste_chemin_fichiers_csv:
		print(f)
		chemin = "/".join(f.split("/")[:-1])+'/'
		# print(chemin)
		basename = os.path.basename(f)
		if basename.endswith("4e.csv") :
			# print(basename)
			df_maj = csv_to_df(chemin,basename)
			list_maj = df_maj["sent"].to_list()
		else:
			df = csv_to_df(chemin, basename)
			list_orig = df["sent"].to_list()
	# a.difference(b) : élé de a qui ne sont pas dans b
	ens_orig = set(list_orig)
	ens_nveau = set(list_maj)
	pas_dans_nveau = ens_orig.difference(ens_nveau)
	pas_dans_orig = ens_nveau.difference(ens_orig)
	
	# print_df(df_maj)
	# print_df(df)
	print(len(pas_dans_nveau))
	print("\nCe qui est dans la liste d'origine et pas dans la nouvelle liste :")
	print(list(pas_dans_nveau))

	print(len(pas_dans_orig))
	print("\nCe qui est dans la nouvelle liste et pas dans la liste d'origine :")
	print(list(pas_dans_orig))


	# 	df_sans = manip_csv.csv_to_df(chemin_sans, nom_sans)
	# 	list_orig = df_avec["sent"].to_list()
	# 	list_sans = df_sans["sent"].to_list()
	# 	# print('_'.join(nom_avec.split('_')[2:6]))
	# 	# print('_'.join(nom_sans.split('_')[2:6]))
	# 	assert nom_avec.split('_')[2:5] == nom_sans.split('_')[2:5]
	# 	dans_sans_pas_dans_avec = set(list_sans).difference(set(list_avec))
	return

def verifie_doublons_csv(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col: str):
	df = csv_to_df(chemin_fichier_csv, nom_fichier_csv)
	liste = df[nom_col].to_list()
	print(len(liste))
	ens = set(liste)
	print(len(ens))
	if len(liste) != len(ens):
		print(f"nbre de doublons : {len(liste)-len(ens)}")
		compte_ph = Counter(p for p in liste)
		doublons = [p for p, c in compte_ph.items() if c > 1]
	else:
		print("pas de doublons")
	pprint(doublons)
	return

if __name__ == "__main__":

	# parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
	# parser.add_argument("nom_debat", help = "nom du débat transcrit")
	# args = parser.parse_args()
	# nom_debat = args.nom_debat
	
	chemin_fichier_csv = "../output/csv/"
	# nom_fichier_csv = nom_debat + ".csv"
	# chemin_fichier_json = "../output/json/"

	# csv_to_df(chemin_fichier_csv,nom_fichier_csv)
	# check_csv_cols_nber(chemin_fichier_csv, nom_fichier_csv)
	# nom_col = 'phrase_corrigee'
	# ph_insert = [377,"9332.813832199547 - 9338.593832199547", "02:35:32", "En tout cas, moi je vous accueille et le 9 juin, il faut grouper les voix face à Macron, ni abstention, ni dispersion."]
	# insert_row_in_df(chemin_fichier_csv, nom_fichier_csv, ph_insert, 376)
	

	# list_ph_non_neg = []
	# delete_row(chemin_fichier_csv, nom_fichier_csv,196)
	
	# csv_to_csv(chemin_fichier_csv_depart,chemin_fichier_csv_to_update, nom_fichier_csv)
	# print(del_col(chemin_fichier_csv_to_update, nom_fichier_csv, 'phrase_corrigee'))

	# list_ph_corr = extract_col_csv(chemin_fichier_csv,nom_fichier_csv, nom_col)
	# print(f"list_ph_corr : {list_ph_corr[269:]}")
	
	# chemin_fichier_csv = "../output/csv/annotations_csv/"
	# nom_fichier_csv_final = "ph_neg_debats.csv"
	# single_val = 2
	# single_val = "presidentielles_MacronLepen_tf1"
	# add_single_val_col_to_csv(chemin_fichier_csv,nom_fichier_csv, single_val, 'nbre participants', idx_insert_col=0)
	# add_single_val_col_to_csv(chemin_fichier_csv,nom_fichier_csv, single_val, 'nom_debat', idx_insert_col=0)
	# decale_col_csv(chemin_fichier_csv,nom_fichier_csv,nom_col, 11, 187)
	
	# csv_to_json(chemin_fichier_csv, nom_fichier_csv, chemin_fichier_json, nom_debat)
	# df, col = extract_col_csv(chemin_fichier_csv, nom_debat+"_corr.csv", "phrase_corrigee")
	# print(type(col))
	# print(col[320])
	# # insertion de la correction
	# col.insert(320,"L'Europe, c'est pas seulement un acteur de guerre, ça doit être un acteur de paix et on doit rechercher la paix." )
	# print(col[319:322])
	# list_ph_corrigee = [(14, "Vous avez pas envie que les géants du numérique qui paient moins d'impôts que le boulanger du coin contribuent ?"), (15, "Vous n'avez pas envie que les entreprises chinoises qui polluent contribuent ?"), (16, 'Je ne vous fais pas confiance en matière économique.'), (17, "Est-ce que l'agenda français n'est pas en train de vous gêner dans votre campagne européenne ?"), (18, 'ça a un lien Madame Hayet'), (19, "Vous n'avez pas tous parlé pour l'instant."), (20, "Marion Maréchal, vous aviez interpellé tout à l'heure Valérie Hayet, notamment sur le gaz, en pointant du doigt que c'était du gaz azerbaïdjanais, pour ceux qui l'auraient pas entendu ici sur le plateau."), (21, "Vous ne voulez pas l'entendre, on parle du quotidien des Français."), (22, "À un moment donné, le pouvoir d'achat, au-delà de les endetter et de créer des impôts européens, c'est d'abord ce que l'État ne vous prend pas."), (23, "Donc évidemment que aujourd'hui, le drame des ménages qui aujourd'hui remplissent leur impôt sur le revenu, c'est pas le cadre de la fiscalité européenne qui n'est pas encore en place, c'est d'abord le choix, et les choix fiscaux, évidemment, de ce gouvernement."), (24, "Alors, parlons-en des salariés, c'est très intéressant."), (25, "J'ai rien vandalisé, Mme Maréchal."), (26, "J'ai rien vandalisé."), (27, "Donc, excusez-moi, mais c'est pas en allant diaboliser des entreprises qui aujourd'hui sont des grandes entreprises, qui, oui gagnent de l'argent et heureusement qu'il y en a et qui font en sorte que 80% de leurs salariés, aujourd'hui, sont des actionnaires qui bénéficient d'ailleurs d'un retour sur investissement, qu'on va régler le pouvoir d'achat."), (28, '100% idéologie et en aucun cas la défense du climat.'), (29, "Et plus de sécurité sociale, ça veut dire plus de droits à la retraite, ça veut dire plus d'assurance maladie, ça veut dire que c'est le système à l'américaine, ce que nous ne dépenserons pas dans les cotisations sociales, ça sera multiplié par deux et par trois."), (30, "Donc, on voit bien là que le bilan des Macronistes c'est non seulement la ruine de l'économie française, des Français abandonnés devant le mur de l'inflation et un endettement qui n'est plus seulement français mais qui est désormais européen."), (31, 'Vous voulez pas rentrer dans le débat.'), (32, 'Il y a pas eu une réponse là-dessus.'), (33, "Parce que aujourd'hui, les subventions vont au plus gros et ne permettent pas, et on parle quand même d'un tiers du budget européen, ne permettent pas, aux petits éleveurs, aux petits agriculteurs, de vivre."), (34, "Parce que aujourd'hui, les producteurs n'arrivent pas à vivre de leur travail et les consommateurs voient les prix augmenter."), (35, "Parce que quand les prix augmentent, eh bien en réalité les producteurs ne touchent plus les dividendes de l'augmentation des prix, ce sont les acteurs de l'agrobusiness qui le font."), (36, "C'est-à-dire que ce soit pas seulement une taxe française mais une taxe européenne ?"), (37, "Pour tous ceux qui nous regardent et qui nous écoutent, l'Union européenne a beaucoup de pouvoir mais elle ne peut pas lever l'impôt."), (38, "Pas le pêcheur de l'île de Ré hein, euh pas la personne qui a hérité d'une maison.")]
	# nom_col = 'phrase_corrigee'	
	# # insérer dans la liste la ph corrigee
	# # add_col_to_csv(chemin_fichier_csv, nom_fichier_csv,list_ph_corrigee,290)
	# insert_data_in_df_col(chemin_fichier_csv, nom_fichier_csv,nom_col,list_ph_corrigee,14)
	# # compare_df_col(chemin_fichier_csv1, fichier1, chemin_fichier_csv2, fichier2, "sent")
	
	# liste_fichiers_csv = glob.glob(chemin_fichier_csv + '*.csv')
	# print(liste_fichiers_csv)
	# df = concat_csv(liste_fichiers_csv)
	
	# df_to_csv(chemin_fichier_csv, nom_fichier_csv_final, df)
	# del_col(chemin_fichier_csv, nom_fichier_csv_final, "sent")
	chemin_fichier_csv = "../output/csv/comparaison/"
	liste_fichiers_csv = glob.glob(chemin_fichier_csv + '*.csv')
	# print(liste_fichiers_csv)
	compare_2_csv_cols(liste_fichiers_csv)

	# verifie_doublons_csv(chemin_fichier_csv, nom_fichier_csv_final, 'phrase_corrigee')