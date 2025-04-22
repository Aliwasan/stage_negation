
# Fonctions de filtrage qui prennent en entrée une phrase qui est un SpacyDoc et la phrase d'origine.
# ON FILTRE CE QUE L'ON NE VEUT PAS

# FILTRAGE pour 'pas' qque soit la polarité
# if doc_token == 'pas'
def pas_precede_DET_NUM(doc_ph, doc_token, index: int):
	return doc_token.text.lower() == "pas" and (
			doc_ph[index-1].pos_ == "DET" or doc_ph[index-1].pos_ == "NUM"
			)

# FILTRAGE DES FAUX POSITIFS (dans Polarity=Neg)
def pas_deb_ph(doc_ph):
	return any(t.text.lower() == "pas" for t in doc_ph[:2])
		
def inf_precede_negateur(doc_ph, doc_token, index: int, forme: str, win_size: int):
	""" 
		Input : la phrase au format doc Spacy
				le token spacy
				indice du négateur dans la phrase segmentée
				taille de la fenêtre
		Vérifie un verbe conjugué (VerbForm=Fin) est présent dans la fenêtre de n tokens avant le mot forme (le négateur). 
		si oui vérifie si un verbe à l'infinitif (VerbForm=Inf) est présent entre le verbe conjugué et le mot forme.
		auquel cas on l'écarte
		si non vérifie si le verbe conjugué est présent dans la fenêtre de n tokens avant le mot forme (le négateur).
	"""
	if doc_token.text.lower() == forme:
		if len(doc_ph[:index]) > win_size:
			empan_avant = [str(t.morph) for t in doc_ph][index-win_size:index]
			empan_avant_str = ' '.join(empan_avant)
			if 'VerbForm=Fin' in empan_avant_str:
				for e in empan_avant:
					if 'VerbForm=Fin' in e: # on va jusqu'à la forme conjuguée pour déterminer l'empan
						idx_verb_conj = empan_avant.index(e)
						if 'VerbForm=Inf' in empan_avant[idx_verb_conj:]:
							# verbe Inf entre le verbe conjugué et le négateur
							return True
						elif 'VerbForm=Inf' in empan_avant[:idx_verb_conj]:
							# print(f"verbe à l'infinitif avant le verbe conjugué et le négateur {forme}.")
							return False
						else:
							# print(f"le token '{forme}' n'est pas précédé d'un 'VerbForm=Inf' dans la fenêtre suivante :\n{doc_ph[index-win_size:index]}\n")
							return False
					else:
						continue
			else:
				if 'VerbForm=Inf' in empan_avant:
					return True
				# else:
				# 	return False
		else: # la taille de la fenêtre est plus grande que l'empan de la ph jusqu'au token
			empan_avant = [str(t.morph) for t in doc_ph][:index]
			# print(f"empan : {empan}")
			if 'VerbForm=Inf' in empan_avant:
				# print(f"le token '{forme}' est précédé d'un 'VerbForm=Inf' dans la fenêtre suivante :\n{doc_ph[:index]}\n")
				return True
			# else:
			# 	# print(f"le token '{forme}' n'est pas précédé d'un 'VerbForm=Inf' dans la fenêtre suivante :\n{doc_ph[:index]}\n")
			# 	return False

# FILTRAGE DES VRAIS NÉGATIFS (Pas de polarity)
def rien_vrai_neg(doc_ph, doc_token, index: int):
	return doc_token.text.lower() == "rien" and (
		doc_ph[index+1:index+2].text.lower() == ","
		or doc_ph[index-1:index].text.lower() == "de"
		or doc_ph[index-1:index].text.lower() == "pour"
		or doc_ph[index+1:index+2].text.lower() == "que"
		or doc_ph[index+1:index+3].text.lower() == "à voir"
		)

def ou_et_mais_etc_pas(doc_ph, doc_token, index: int):
	""" 'et alors', 'et bien' etc. suivis de pas
		ex : 'et bien pas moi'
		virgule précède 'pas' 
		ex : ', pas vous personnellement,'
	"""
	return doc_token.text.lower() == "pas" and (
		doc_ph[index-1:index].text.lower() == "ou" \
   		or doc_ph[index-1:index].text.lower() == "et"\
		or doc_ph[index-2:index-1].text.lower() == "et"\
		or doc_ph[index-1:index].text.lower() == "mais"\
		or doc_ph[index-1:index].text.lower() == "non"\
		or doc_ph[index-1:index].text.lower() == "pourquoi"\
		or doc_ph[index-1:index].text.lower() == ","
		)

def pas_suivi_adj(doc_ph, doc_token, index: int):
	""" 'pas' est suivi d'un ADJ, ex : 'qui nous permettait d'avoir une énergie pas chère.' """
	return doc_token.text.lower() == 'pas' and doc_ph[index+1].pos_ == 'ADJ'

# FILTRAGE DES EXPRESSIONS figées en 'pas'	
def exp_pas(doc_ph, doc_token, index: int):
	""" teste si 'pas' est suivi de 'un mot' ou de 'plus tard"""
	return doc_token.text.lower() == "pas" and (
			doc_ph[index+1:index+3].text.lower() == "un mot"\
   			or doc_ph[index+1:index+3].text.lower() == "plus tard"
			)

def pos_personne(doc_token):
	""" Vérifie si le token 'personne' est un NOUN """
	return doc_token.text.lower() == 'personne' and doc_token.pos_ =='NOUN'

def comme_jamais(doc_ph, doc_token, index: int):
	return doc_token.text.lower() == "jamais" and doc_ph[index-1].text.lower() == "comme"

def sans_foi_ni_loi(doc_ph, doc_token, index: int):
	return doc_token.text.lower() == "ni" and doc_ph[index-1].text.lower() == "foi"