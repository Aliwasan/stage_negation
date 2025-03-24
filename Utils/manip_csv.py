import argparse
import polars as pl
import csv
import json

def reindex_liste(list_a_reindexer: list[tuple], ecart: int):
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

def df_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, df):
	""" Prend un df et en fait un csv"""
	df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return

def csv_to_df(chemin_fichier_csv: str, nom_fichier_csv: str):
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv,truncate_ragged_lines=True) #schema={'n_ph': i64,'horo': str,'hms': str,'sent': str,'phrase_corrigee': str}
	with pl.Config(tbl_rows=-1):
		print(df)
	return df

def json_to_csv(chemin_fichier_csv: str, chemin_fichier_json: str, nom_debat: str):
	# TODO
	return

def csv_to_json(chemin_fichier_csv: str, nom_fichier_csv: str, chemin_fichier_json: str, nom_debat: str):
	""" on est parfois amené à faire un json pour refaire l'horo_transcr_ph_neg() après une insertion/modification
		pour mettre à jour les fichiers audio et txt
	"""
	# df = csv_to_df(chemin_fichier_csv, nom_fichier_csv)
	# df.write_ndjson(chemin_fichier_json+nom_debat+'.json')	
	#TODO : ne pas utiliser write_ndjson car ne sérialise pas bien il faut refaire un json à partie d'un dico à remplir à partir
	# de csv.reader() qui tranforme chaque rang du csv en liste
	list_ph_neg = []
	with open(chemin_fichier_csv+nom_fichier_csv, 'r') as f:
		lecture = csv.reader(f, delimiter=',')
		list_ph_neg = [p for p in lecture]
	
	list_cles = list_ph_neg[0]
	list_ph_neg.pop(0)
	print(list_ph_neg)
	# on fait un json
	data_list = []
	for item in list_ph_neg:
		json_dic = {}
		json_dic[list_cles[0]] = item[0]
		json_dic[list_cles[1]] = item[1]
		json_dic[list_cles[2]] = item[2]
		json_dic[list_cles[3]] = item[3]
		data_list.append(json_dic)
	with open(chemin_fichier_json+nom_debat+'.json', 'w') as output_json:
		json.dump(data_list, output_json, indent=4)
	return

def extract_col_csv(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col: str):
	""" Prend un csv en extrait au format list la colonne dont le nom est donné en arg"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	print(df)
	to_update_column = df[nom_col].to_list()
	return df, to_update_column

def decale_rang_col_csv(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col: str, nb_rang_decal: int, start_index=None):
	""" Prend un csv en extrait la colonne dont le nom est donné en arg
		la réinsère à p. d'un rang plus bas dont l'index est donné en arg
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	col = df[nom_col].to_list()
	# print(col)
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
	with pl.Config(tbl_rows=-1):
		print(df)
	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplacera le précédent le cas échéant
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return

def del_col(chemin_fichier_csv: str, nom_fichier_csv: str, col_name: str, start_index=None):
	"""opens a csv, delete a col, writes the new csv, returns the df"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	if start_index != None:
		df = df.drop(col_name[start_index:])
	else:	
		df = df.drop(col_name)
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return df

def add_col_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_ph: list, start_index=None):
	""" Insère une colonne de donnée d'un df au format list à un fichier csv préexistant:
		début de correction des phrases d'un débat.
		ou
		Insère des données dans une colonne spécifique à partir d'un index de rang donné: 
		suite de la correction des phrases d'un débat.
	"""
	list_ph = [p[1] for p in list_ph]
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
		# rappel: les rangs commencent bien à 1 mais ici on est dans une liste de la col existante
		# par ex : si on veut insérer au rang 33, c'est à l'indice 32
		start_index -= 1
		print(f"start_index dans la liste de la col :{start_index}")
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
		df.insert_column(4, s) # on insère la col à la suite des cols existantes
		with pl.Config(tbl_rows=-1):
			print(f"df nouveau débat :\n {df}")

	# Sauvegarder le DataFrame modifié dans un fichier CSV qui remplacera le précédent le cas échéant
	df_to_csv(chemin_fichier_csv, nom_fichier_csv, df)
	return

def insert_row_in_df(chemin_fichier_csv: str, nom_fichier_csv: str, list_to_insert: list, insert_index=None ):
	""" insère un ou plusieurs rangs à un csv en faisant donc attention à l'indexation préexistante
		l'index d'insertion doit être le n° de la phrase avant celle que l'on veut insérer
	"""
	df = pl.read_csv(chemin_fichier_csv+nom_fichier_csv)
	# Ajout d'une valeur nulle pour la col "ph_corrigee"
	list_to_insert.append("N/A")
	
	if insert_index >= df.height:
		raise ValueError("L'index de départ est supérieur à la hauteur du DataFrame.")
	# vérification que la serie ait le même nbre de cols sur le rang d'avant l'insertion par ex
	if len(list_to_insert) != len(df.row(insert_index-1)):
			raise ValueError("Le nombre de valeurs à insérer est différent au nbre de cols du DataFrame.")
	
	nom_cols = ["n_ph","horo", "hms", "sent", "phrase_corrigee"]
	dic_to_insert = {}
	for a, b in zip(nom_cols, list_to_insert):
		dic_to_insert[a] = b

	# création d'un df avec les données à insérer
	df_to_insert = pl.DataFrame(dic_to_insert)
	
	# Pour insérer on est obligé de scinder puis de concaténer

	# Split the dataframe
	df_before = df.slice(0, insert_index)  # Rows before insert index
	df_after = df.slice(insert_index, df.height - insert_index)  # Rows after insert index
	# print(df_before)
	# print(df_after)

	# reindexation des n_ph du bloc scindé après l'insertion
	list_index = df_after["n_ph"].to_list()
	list_index = [i+1 for i in list_index]
	# print(list_index)
	series_index = pl.Series("n_ph", list_index)
	df_after.replace_column(0, series_index)

	# Concatenate the three parts
	nveau_df = pl.concat([df_before, df_to_insert, df_after])
	# with pl.Config(tbl_rows=-1):
	# 	print(nveau_df)
	nveau_df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return

def insert_data_in_col(chemin_fichier_csv: str, nom_fichier_csv: str, nom_col_insertion: str, list_to_insert: list, insert_index=None ):
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
	to_update_column[insert_index:insert_index + len(list_to_insert)] = list_to_insert
	print(f"len de la nouvelle colonne :{len(to_update_column)}")
	print(to_update_column)
	print(len(to_update_column))
	df = df.with_columns(pl.Series('phrase_corrigee', to_update_column))
	with pl.Config(tbl_rows=-1):
		print(df)
	df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return

def delete_row(chemin_fichier_csv: str, nom_fichier_csv: str, delete_index=None):
	""" efface un rang d'un csv en faisant et réindexe les rangs suivant le rang effacé
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

	# Concatenate the three parts
	nveau_df = pl.concat([df_before, df_after])
	with pl.Config(tbl_rows=-1):
		print(nveau_df)
	nveau_df.write_csv(chemin_fichier_csv+nom_fichier_csv, null_value="N/A")
	return

def select_cols_to_csv(chemin_fichier_csv: str, nom_fichier_csv: str, list_noms_cols: list[str], \
					   chemin_nveau_fichier_csv: str, nom_nveau_fichier_csv: str):
	df = csv_to_df(chemin_fichier_csv, nom_fichier_csv)
	df_selected_cols = df.select(list_noms_cols)
	with pl.Config(tbl_rows=-1):
		print(df_selected_cols)
	print(df_selected_cols)
	df_to_csv(chemin_nveau_fichier_csv, nom_nveau_fichier_csv, df_selected_cols)
	return
	
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
	parser.add_argument("nom_debat", help = "nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat
	
	chemin_fichier_csv = "../output/csv/"
	nom_fichier_csv = nom_debat + ".csv"
# 	# chemin_fichier_json = "../output/json/"

# 	# csv_to_df(chemin_fichier_csv,nom_fichier_csv)
# 	# check_csv_cols_nber(chemin_fichier_csv, nom_fichier_csv)
# 	nom_col = 'phrase_corrigee'
	# ph_insert = [377,"9332.813832199547 - 9338.593832199547", "02:35:32", "En tout cas, moi je vous accueille et le 9 juin, il faut grouper les voix face à Macron, ni abstention, ni dispersion."]
	# insert_row(chemin_fichier_csv, nom_fichier_csv, ph_insert, 376)

	# delete_row(chemin_fichier_csv, nom_fichier_csv,370)
	# csv_to_csv(chemin_fichier_csv_depart,chemin_fichier_csv_to_update, nom_fichier_csv)
	# print(del_col(chemin_fichier_csv_to_update, nom_fichier_csv, 'phrase_corrigee'))

	# list_ph_corr = extract_col_csv(chemin_fichier_csv,nom_fichier_csv, nom_col)
	# print(f"list_ph_corr : {list_ph_corr[269:]}")
	#
	# del_col(chemin_fichier_csv, nom_fichier_csv, "phrase_corrigee")
	# add_to_csv(chemin_fichier_csv,nom_fichier_csv, list_to_insert,270)

	# decale_col_csv(chemin_fichier_csv,nom_fichier_csv,nom_col, 11, 187)
	
	# csv_to_json(chemin_fichier_csv, nom_fichier_csv, chemin_fichier_json, nom_debat)
	# df, col = extract_col_csv(chemin_fichier_csv, nom_debat+"_corr.csv", "phrase_corrigee")
	# print(type(col))
	# print(col[320])
	# # insertion de la correction
	# col.insert(320,"L'Europe, c'est pas seulement un acteur de guerre, ça doit être un acteur de paix et on doit rechercher la paix." )
	# print(col[319:322])

	# insérer dans la liste la ph corrigee
	# add_col_to_csv(chemin_fichier_csv, nom_fichier_csv,list_ph_corrigee,290)
	# insert_data_in_col(chemin_fichier_csv, nom_fichier_csv,nom_col,list_ph_corrigee,187)