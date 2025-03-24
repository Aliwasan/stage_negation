
def concat_seg_horo(chemin:str, fichier:str) -> list[tuple]:
	"""
	Lit le fichier de transcriptions ligne par ligne
	et remplit une liste de tuples (horodateur, texte de la phrase)
	si la phrase est sur plusieurs lignes de transcription, fusionne les lignes de début de milieu et de fin
	prend l'horadeur du début et de fin de la phrase
	"""
	transcripts_list = []
	texte_phrase = ""
	
	with open(chemin+fichier, 'r') as f_in:
		# la première ligne 
		l = f_in.readline()
		s = l.split(":  ")
		horo_deb = s[0].split(" - ")[0]
		# print(horo_deb)
		horo_fin = s[0].split(" - ")[1]
		# print(horo_fin)
		texte_seg = s[1]
		horo = horo_deb + " - " + horo_fin
		transcripts_list.append((horo,texte_seg.strip()))
		for l in f_in.readlines(): # liste des segments horodatés
			try:
				# s = l[l.index(":")+3:]
				s = l.split(":  ")
				horo_deb = s[0].split(" - ")[0]
				horo_fin = s[0].split(" - ")[1]
				texte_seg = s[1]
				# print(f"horo_deb : {horo_deb}, horo_fin : {horo_fin}, seg : {texte_seg}")
				
				# début de la boucle des 4 cas le seg "constitue"
				# si le segment commence par une maj ou un tiret et se termine par un marqueur de fin de phrase
				# phrase complète 
				if (texte_seg[0].isupper() or texte_seg[0].startswith("–")) and texte_seg[-2:].strip() in ["?", ".", "…"]:
					if texte_phrase == "":
						horo = horo_deb + " - " + horo_fin
						texte_phrase += texte_seg									
						transcripts_list.append((horo,texte_phrase.strip()))
						texte_phrase = ""
						horo = ""
					else: # la ph précédente pas terminée par marqueur
						# on la termine
						horo = horo + horo_deb # la borne de fin doit être la borne de début du segment courant
						transcripts_list.append((horo,texte_phrase.strip()))
						texte_phrase = ""
						# démarre une nouvelle phrase avec le segment courant
						horo = horo_deb + " - "
						texte_phrase += texte_seg.strip() + " "
				# si le segment commence par une majuscule ou un tiret et ne se termine pas par un marqueur de fin de phrase
				# on commence la phrase
				# on doit tester aussi si on est pas déjà dans une phrase ?
				elif (texte_seg[0].isupper() or texte_seg[0].startswith("–")) and texte_seg[-2:].strip() not in ["?", ".", "…"]:
					if texte_phrase == "": #ph précé bien terminée
						horo = horo_deb + " - "
						texte_phrase += texte_seg.strip() + " "
					else: # on est dans une phrase entamée
						# on la termine
						horo = horo + horo_deb # la borne de fin doit être la borne de début du segment courant
						transcripts_list.append((horo,texte_phrase.strip()))
						texte_phrase = ""
						# on démarre une phrase
						horo = horo_deb + " - "
						texte_phrase += texte_seg.strip() + " "
				# si le segment commence par une minuscule ou un chiffre ou un guillemet et ne se termine pas par un marqueur de fin de phrase
				# on est dans la phrase
				elif (texte_seg[0].islower() or texte_seg[0].isdigit() or texte_seg[0].startswith('«')) and texte_seg[-2:].strip() not in ["?", ".", "…"]:
					if texte_phrase == "": #il y avait une phra terminée avant et donc on doit commencer une nouvelle phrase
						horo = horo_deb + " - "
						texte_phrase += texte_seg.strip() + " "
					else: #on continue la phrase
						texte_phrase += texte_seg.strip() + " "
				# dernier cas: la phrase commence par une minuscule ou un chiffre ou un guillemet et se termine par un marqueur de fin de phrase
				# on termine la phrase
				elif (texte_seg[0].islower() or texte_seg[0].isdigit() or texte_seg[0].startswith('«')) and texte_seg[-2:].strip() in ["?", ".", "…"]:
					if texte_phrase == "": # on crée une ph entière
						horo = horo_deb + " - " + horo_fin
						transcripts_list.append((horo, texte_seg.strip()))
						horo = ""
					else: # on termine la ph
						horo = horo + horo_fin
						texte_phrase += texte_seg.strip()
						transcripts_list.append((horo, texte_phrase.strip()))
						texte_phrase = ""
						horo = ""
				else:
					print(f"dernier cas non connu l : {l}")
					pass
			except IndexError:
				print(f"IndexError : horo : {horo}, texte_seg : {texte_seg}")
				pass
			# except AssertionError:
			# 	print(f"assert texte_phrase != '' : {l}")
	return transcripts_list