import datetime
from glob import glob
import os
import pathlib
from pathlib import Path
import regex
import termios

def vider_buffer():
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def sec2hms(seconds): # TODO : ajouter les types
	""" Input: un horodatage de Whisper() en secondes au format string avec parfois 13 chiffres après la virgule
	ex : 219.79999999999998
	en fonction du format liste de float, string ou float
	Output: l'horodatage convertit en heures, minutes et secondes format str ex: 00:00:37 - 00:00:40
	"""
	if isinstance(seconds, list) == True:
		list_hms = []
		for t in seconds:
			# Conversion en heures, minutes, secondes 
			h = int(t // 3600) # Diviser par 3600 pour obtenir les heures
			m = int((t % 3600) // 60) # Diviser le reste par 60 pour obtenir les minutes
			s = int(t % 60) # Le reste des secondes
			list_hms.append(f"{h:02d}:{m:02d}:{s:02d}")
		return list_hms
	elif isinstance(seconds, str) and "-" in seconds:
		sec = float(seconds.split(' - ')[0])
		# Conversion en heures, minutes, secondes 
		h = int(sec // 3600) # Diviser par 3600 pour obtenir les heures
		m = int((sec % 3600) // 60) # Diviser le reste par 60 pour obtenir les minutes
		s = int(sec % 60) # Le reste des secondes
		return f"{h:02d}:{m:02d}:{s:02d}"
	else:
		# Conversion en heures, minutes, secondes 
		h = int(seconds // 3600) # Diviser par 3600 pour obtenir les heures
		m = int((seconds % 3600) // 60) # Diviser le reste par 60 pour obtenir les minutes
		s = int(seconds % 60) # Le reste des secondes
		return f"{h:02d}:{m:02d}:{s:02d}"

def cumul_hms(h_list: list[str]):
	"""	Prend une liste de strings au format hms
		additionne les heures, minutes et secondes
	"""
	cumul = datetime.timedelta()
	for e in h_list:
		(h, m, s) = e.split(':')
		d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
		cumul += d
	return str(cumul)

def diff_hms(h_tup: tuple[str]):
	"""	Prend un tuple de 2 strings au format hms
		calcule le delta entre les heures, minutes et secondes
	"""
	(h, m, s) = h_tup[0].split(':')
	h1 = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
	(h, m, s) = h_tup[1].split(':')
	h2 = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
	diff = h2 - h1
	return diff

def convert2millisec(hms:str):
	""" Prend un horodateur au format h:m:s et le convertit 
		en un horodateur au format millisecondes uniquement
	"""
	h, m, s = float(hms[0])*3600000, float(hms[1])*60000, float(hms[2])*1000
	# print(h, m, s)
	heure = h + m + s
	# print(heure)
	return heure

def delta_end_start(horo_deb: str, horo_fin_prec: str): 
    return float(horo_deb) - float(horo_fin_prec)

def cumul_delta_borne_end_start(chemin_fichier: str, fichier: str):
    """ Lit la borne de fin de la première ligne du fichier de transcription
		puis pour chaque segment:
        calcule la différence entre la borne de fin de chaque segment précédent avec la borne de début du segment courant
        renvoie le nbre de fois où il y a un écart (delta != 0.0) et le temps des écarts total pour le fichier en sec
    """
    with open(chemin_fichier + fichier) as f:
        cpteur_delta = 0.0
        cumul_delta = 0.0 
        horo_fin = ""
        liste_lignes = f.readlines()
        for ligne in liste_lignes:
            horo_deb = ligne.split(':')[0].split(' - ')[0]
            # print(ligne)
            if ligne:
                if horo_deb == "0.0":
                    horo_fin = ligne.split(':')[0].split(' - ')[1]
                    print(f"horo_fin_premiere_ligne : {horo_fin}")
                    # print(horo_deb, horo_fin)
                else:
                    print("deuxième ligne et plus")
                    horo_deb = ligne.split(':')[0].split(' - ')[0]
                    horo_fin = horo_fin
                    print(horo_deb, horo_fin)
                    d = delta_end_start(horo_deb, horo_fin)
                    print(f"delta : {d}")
                    if d != 0.0:
                        print(f"delta: {d}")
                        cpteur_delta += 1
                        cumul_delta += d
                    horo_fin = ligne.split(':')[0].split(' - ')[1]
                    print(horo_deb, horo_fin)     
    return cpteur_delta, cumul_delta

def delta_secondes(horo: tuple[float]):
	diff = float(horo[0] - horo[1])
	return diff

def rep_liste(chemin_rep:str, extension:str):
    """ Itère sur les fichiers d'une extension donnée (ex : ".mp3")
        dans un répertoire donné.
        Renvoie la liste ordonnée par ordre ascii des noms de fichiers dans le répertoire
    """
    liste = glob(chemin_rep + '*' + extension)
    liste_ord = sorted([e.split('/')[-1] for e in liste]) # 01europennes_europe1.mp3
    return liste_ord

def taille_fichier_mots(chemin_fichier: str, nom_fichier: str):
	"""
		ouvre un fichier
		lit chaque ligne et remplaçe les ponctuations avant de la tokenizer.
		retourne le nbre de toks
	"""
	cpteur_toks = 0
	for ligne in open(chemin_fichier + nom_fichier):
		if ligne != '\n':
			ligne = regex.sub(r"\P{Letter}"," " , ligne) # \P{nom classe} : tout ce qui n'est pas des lettres ici équiv à : ligne = re.sub(r"[.,:;'_\-\(\)!\"\/\[\]]"," " , l)
			ligne = ligne.strip().split(' ')
			# print(ligne)
			len_ligne = len([t for t in ligne if t != ' ' and t != ''])
			cpteur_toks += len_ligne
	return cpteur_toks

def rename_dir(chemin_rep: str, ancien_nom: str, nveau_nom: str):
	""" renomme le répertoire contenu dans le rep au bout du chemin donné en arg"""
	os.chdir(chemin_rep)
	os.rename(nveau_nom,ancien_nom)
	return

def rename_dir_file(chemin_rep, ancien_nom_fichier: str, nveau_nom_fichier: str):
	""" renomme le fichier contenu dans le rep au bout du chemin donné en arg"""
	# os.chdir(chemin_rep)
	os.rename(os.path.join(chemin_rep,ancien_nom_fichier), os.path.join(chemin_rep, nveau_nom_fichier))
	return


if __name__ == "__main__":
	
	# print(sec2hms(2598.674240362812))
	# list_hms = ['00:59:47', '00:59:50'] # 00:39:52
	# # print(cumul_hms(list_hms))
	# tup_hms = ['00:19:58', '00:20:09']
	# print(diff_hms(tup_hms))

	chemin_fichier = "../output/debat_entier/presidentielles_MacronLepen_tf1/"
	# nom_fichier = "presidentielles_MacronLepen_tf1_texte_entier.txt"

	# d = cumul_delta_borne_end_start(chemin_fichier, nom_fichier)
	# print(d)
	
	# print(delta_secondes((8388.169365079366, 8388.173832199547)))

	# seconds = "582.56 - 583.68"
	# print(sec2hms(seconds))
	
	# print(taille_fichier_mots(chemin_fichier, nom_fichier))