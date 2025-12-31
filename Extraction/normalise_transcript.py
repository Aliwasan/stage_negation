
def point_milieu(seg: str):
	return '.' in seg.strip()[:-4] and seg[seg.index('.')-1] != 'M'

def scission_point(seg: str):
	empan_avant = seg[:seg.index('.')+1]
	empan_apres = seg[seg.index('.')+1:].strip()
	return empan_avant, empan_apres

def concat_seg_horo(nom_rep: str, fichier:str) -> list[tuple]:
	"""
		Input : fichier .txt où chaque ligne est un segment de transcription précédé de son horodateur (début - fin)
		Lit le fichier de segments de transcriptions ligne par ligne
		- concatène les lignes de début de milieu et de fin de phrase en s'appuyant sur les marqueurs de fin de phrase
		- prend l'horadeur du début et de fin de la phrase
		Output : une liste de tuples (horodateur, texte de la phrase)
	"""
	transcripts_list = []
	texte_phrase = ""
	
	with open(nom_rep + fichier, 'r') as f_in:
		# la première ligne 
		l = f_in.readline()
		s = l.split(":  ")
		horo_deb = s[0].split(" - ")[0]
		horo_fin = s[0].split(" - ")[1]
		texte_seg = s[1]
		horo = horo_deb + " - " + horo_fin
		transcripts_list.append((horo,texte_seg.strip()))
		for l in f_in.readlines(): # liste des segments horodatés
			try:
				s = l.split(":  ")
				horo_deb = s[0].split(" - ")[0]
				horo_fin = s[0].split(" - ")[1]
				texte_seg = s[1]
				if point_milieu(texte_seg):
					emp_av, emp_ap = scission_point(texte_seg)
					if texte_phrase == "":
						horo = horo_deb + " - " + horo_fin
						texte_phrase += emp_av
						transcripts_list.append((horo,texte_phrase.strip()))
						texte_phrase = ""
						horo = horo_fin + " - "
						texte_phrase += emp_ap.strip() + " "
					else:
						horo = horo + horo_deb
						texte_phrase += emp_av
						transcripts_list.append((horo,texte_phrase.strip()))
						texte_phrase = ""
						horo = horo_fin + " - "
						texte_phrase += emp_ap.strip() + " "
				else:
					if (texte_seg[0].isupper() or texte_seg[0].startswith("–")) and texte_seg[-2:].strip() in ["?", ".", "…", '!']:
						if texte_phrase == "":
							horo = horo_deb + " - " + horo_fin
							texte_phrase += texte_seg									
							transcripts_list.append((horo,texte_phrase.strip()))
							texte_phrase = ""
							horo = ""
						else:
							horo = horo + horo_deb
							transcripts_list.append((horo,texte_phrase.strip()))
							texte_phrase = ""
							horo = horo_deb + " - "
							texte_phrase += texte_seg.strip() + " "
					elif (texte_seg[0].isupper() or texte_seg[0].startswith("–")) and texte_seg[-2:].strip() not in ["?", ".", "…", '!']:
						if texte_phrase == "":
							horo = horo_deb + " - "
							texte_phrase += texte_seg.strip() + " "
						else:
							horo = horo + horo_deb
							transcripts_list.append((horo,texte_phrase.strip()))
							texte_phrase = ""
							horo = horo_deb + " - "
							texte_phrase += texte_seg.strip() + " "
					elif (texte_seg[0].islower() or texte_seg[0].isdigit() or texte_seg[0].startswith('«')) and texte_seg[-2:].strip() not in ["?", ".", "…", '!']:
						if texte_phrase == "":
							horo = horo_deb + " - "
							texte_phrase += texte_seg.strip() + " "
						else:
							texte_phrase += texte_seg.strip() + " "
					elif (texte_seg[0].islower() or texte_seg[0].isdigit() or texte_seg[0].startswith('«')) and texte_seg[-2:].strip() in ["?", ".", "…", '!']:
						if texte_phrase == "":
							horo = horo_deb + " - " + horo_fin
							transcripts_list.append((horo, texte_seg.strip()))
							horo = ""
						else:
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
	return transcripts_list