
# Fonctions de filtrage qui prennent en entrée une phrase qui est un SpacyDoc et la phrase d'origine.
# ON FILTRE CE QUE L'ON NE VEUT PAS


# FILTRAGE DES FAUX POSITIFS
def pas_deb_ph(doc_ph, doc_token, str_ph: str):
	""" ph est une SpacyDoc """
	deb_ph = str_ph.split()[0:2]
	for doc_token in doc_ph:
		if doc_token.text.lower() == "pas" and doc_token.text in deb_ph:
			return True
		
def inf_precede_pas(doc_ph, doc_token, index: int, morph_tag: str, forme: str, win_size: int):
	""" Vérifie si le tag VerbForm=Fin d'un verbe conjugué est présent dans la fenêtre de n tokens avant le mot forme (le négateur) 
		si oui vérifie si le tag VerbForm=Inf est présent entre le verbe conjugué et le mot forme.
		auquel cas on continue
		si non vérifie si le tag VerbForm=Inf est présent dans la fenêtre de n tokens avant le mot forme (le négateur).

	"""
	if doc_token.text.lower() == forme:
			if len(doc_ph[:index]) > win_size:
				empan = [str(t.morph) for t in doc_ph][index-win_size:index]
				print(f"empan : {empan}")
				empan_str = ' '.join(empan)
				if 'VerbForm=Fin' in empan_str:
					for e in empan:
						if 'VerbForm=Fin' in e:
							idx_verb_conj = empan.index(e)
							if morph_tag in empan[idx_verb_conj:]:
								# le verbe Inf est entre le verbe conjugué et le négateur
								return True
							elif morph_tag in empan[:idx_verb_conj]:
								print(f"verbe à l'infinitif avant le verbe conjugué et le négateur {forme}.")
								return False
							else:
								print(f"le token '{forme}' n'est pas précédé d'un {morph_tag} dans la fenêtre suivante :\n{doc_ph[index-win_size:index]}\n")
								return False
						else:
							pass
				else:
					if morph_tag in empan:
						return True
					else:
						return False
			else: # la taille de la fenêtre est plus grande que l'empan de la ph jusqu'au token
				empan = [str(t.morph) for t in doc_ph][:index]
				print(f"empan : {empan}")
				if morph_tag in empan:
					print(f"le token '{forme}' est précédé d'un {morph_tag} dans la fenêtre suivante :\n{doc_ph[:index]}\n")
					return True
				else:
					print(f"le token '{forme}' n'est pas précédé d'un {morph_tag} dans la fenêtre suivante :\n{doc_ph[:index]}\n")
					return False

# FILTRAGE DES VRAIS NÉGATIFS
def ou_et_pas(doc_ph, doc_token, index: int):
	if doc_token.text.lower() == "pas" and (doc_ph[index-1:index].text.lower() == "ou" or doc_ph[index-1:index].text.lower() == "et"):
		return True

def rien_vrai_neg(doc_ph, doc_token, index: int):
	if doc_token.text.lower() == "rien"\
		and	(doc_ph[index+1:index+2].text.lower() == ","
		or doc_ph[index-1:index].text.lower() == "de"
		or doc_ph[index-1:index].text.lower() == "pour"
		or doc_ph[index+1:index+2].text.lower() == "que"
		or doc_ph[index+1:index+3].text.lower() == "à voir"):
		return True

def personne(doc_ph, doc_token, index: int, win_size: int):
	""" Vérifie si le token 'personne' est précédé d'un DET """
	# if doc_token.text.lower() == 'personne'
	if len(doc_ph[:index])> win_size:
		if 'DET' in [t.pos_ for t in doc_ph][index-win_size:i]:
			return True
		else:
			return False
	else: # la taille de la fenêtre est plus grande que l'empan de la ph jusqu'au token
		if 'DET' in [t.pos_ for t in doc_ph][:index]:
			return True
		else:
			return False

# FILTRAGE DES EXPRESSIONS
def expr_n(doc_ph, doc_token, index: int):
	""" teste si 'n'' est suivi de 'importe' """
	if doc_token.text.lower() == "n'" and doc_ph[index+1:index+2].text.lower() == "importe":
		return True

def exp_pas(doc_ph, doc_token, index: int):
	""" teste si 'pas' est suivi de 'un mot' """
	if doc_token.text.lower() == "pas" and doc_ph[index+1:index+3].text.lower() == "un mot":
		return True

def 