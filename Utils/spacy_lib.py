import argparse
import spacy
import re

def spacy_load_doc(chemin_fichier: str, texte_entier: str, nom_model):
	""" Charge le texte du débat récupéré depuis dico Whisper dans le moteur spacy
		renvoie un objet Doc : <class 'spacy.tokens.doc.Doc'>
	"""
	nlp = spacy.load(nom_model)
	with open(chemin_fichier + texte_entier, 'r', encoding="utf-8") as f:
		texte = f.read()
	# print(len(texte))
	spacy_doc = nlp(texte)
	return spacy_doc

def EN_spacy(spacy_doc, model: str, list_motifs_a_enlever=None):
	""" Prend un spacy doc en entrée, calcule le nombre d'EN et retourne l'ensemble contenant les EN
		après lecture de l'ensemble si il y a des erreurs ont refait tourner la fonction en les enlevant avec 
	"""
	print(f"Modèle : {m}\n")
	list_EN = []
	for e in spacy_doc.ents:
		# print(e.text, e.label_)
		list_EN.append(e.text)
	# print(spacy_doc.ents)
	print(f"nbre d'occurrences d'EN : {len(list_EN)}") # 1539 1611
	set_EN = set(list_EN)
	print(f"nbre d'EN : {len(set_EN)}") # 480 446
	# print(set_EN)
	if list_motifs_a_enlever != None:
		motif = re.compile(r'\b(?:%s)\b' % '|'.join(list_motifs_a_enlever)) #".?ez-moi"
		list_supr = [e for e in set_EN if motif.findall(e)]
		print(list_supr)
		for e in list_supr:
			set_EN.discard(e)
		print(len(set_EN)) # 473 441
		return set_EN
	else:
		print(set_EN)
		return set_EN
	
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="1er argument : nom du débat")
	parser.add_argument("nom_debat", help="nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	chemin_fichier = f"../output/debat_entier/{nom_debat}/"
	nom_fichier = f"{nom_debat}_texte_entier.txt"
	list_models = ["fr_core_news_md","fr_core_news_lg","fr_dep_news_trf"]
	list_ens_EN = []
	
	for m in list_models:
		doc = spacy_load_doc(chemin_fichier, nom_fichier, m)
		list_ens_EN.extend(EN_spacy(doc,m))
	print(f"Différence sym entre les EN modèle 1 et 2 : les EN qui sont dans modèle 2 : {list_ens_EN[1]} et pas dans le 1 : {list_ens_EN[0]} ")
	print({list_ens_EN[0]}.symmetric_difference({list_ens_EN[1]}))

	print(f"Différence sym entre les EN modèle 2 et 1 : les EN qui sont dans modèle 1 : {list_ens_EN[0]} et pas dans le 2 : {list_ens_EN[0]} ")
	print({list_ens_EN[1]}.symmetric_difference({list_ens_EN[0]}))