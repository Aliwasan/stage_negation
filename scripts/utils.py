import datetime
from glob import glob
import os
import spacy
# import fr_core_news_lg

def sec2hms(seconds:list[float]):
	""" Input: un horodatage de Whisper() en secondes au format string avec parfois 13 chiffres après la virgule
	ex : 219.79999999999998
	Output: l'horodatage convertit en heures, minutes et secondes format str ex: 00:00:37 - 00:00:40
	"""
	list_hms = []
	for t in seconds:
		# Conversion en heures, minutes, secondes 
		h = int(t // 3600) # Diviser par 3600 pour obtenir les heures
		m = int((t % 3600) // 60) # Diviser le reste par 60 pour obtenir les minutes
		s = int(t % 60) # Le reste des secondes
		list_hms.append(f"{h:02d}:{m:02d}:{s:02d}")
	return list_hms


    # Python Program to Convert seconds
# into hours, minutes and seconds
    #return str(datetime.timedelta(seconds = float(seconds)))


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

def rep_liste(chemin_rep:str, extension:str):
    """ Itère sur les fichiers d'une extension donnée (ex : ".mp3")
        dans un répertoire donné.
        Renvoie la liste ordonnée par ordre ascii des noms de fichiers dans le répertoire
    """
    liste = glob(chemin_rep + '*' + extension)
    liste_ord = sorted([e.split('/')[-1] for e in liste]) # 01europennes_europe1.mp3
    
    return liste_ord

def spacy_load_doc(chemin_fichier: str, texte_entier: str, nom_model):
	""" Charge le texte du débat récupéré depuis dico Whisper dans le moteur spacy
		renvoie un objet Doc : <class 'spacy.tokens.doc.Doc'>
	"""
	nlp = spacy.load(nom_model)
	with open(chemin_fichier + texte_entier, 'r', encoding="utf-8") as f:
		texte = f.read()
	print(len(texte))
	nlp_doc = nlp(texte)
	return nlp_doc

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

def read_audio_files(chemin_rep_transcript: str, chemin_rep_audio: str):
	""" Ouvre simultanément :
	 - le fichier de la phrase négative transcrite, l'affiche sur le Terminal
	 - le fichier du segment audio correspondant et le lit
	"""
	list_transcripts = sorted(glob.glob(chemin_rep_transcript + '/*.txt'), key=len)
	list_audio = sorted(glob.glob(chemin_rep_audio + '/*.txt'), key=len)
	print(list_transcripts)
	print(list_audio)
	cpteur = 0

	# print(list_audio[int(i)-1])
	while True:
		i = input("\nEntrez le n° de la phrase négative à écouter ou bien faites Enter pour écouter toutes les phrases.\n\
			Si vous voulez quitter taper q + entrée : ")
		if i.isdigit():
		# print(i)
			with open(chemin_rep_transcript+list_transcripts[int(i)+1]) as f:
				print(f"Phrase négative n° {i} :\n")
				print(f.read()+"\n\n")
			sound = AudioSegment.from_file(chemin_rep_audio+list_audio[int(i)+1], format="mp3")
			play(sound)
			s = input("Taper sur q + entrée pour sortir ou entrée pour continuer : ")
			if s == "q":
				break
		else:
			for transcript, audio in zip(list_transcripts, list_audio):
				cpteur += 1
				with open(chemin_rep_transcript+transcript) as f:
					print(f"Phrase négative n° {cpteur} :\n")
					print(f.read()+"\n\n")
				sound = AudioSegment.from_file(chemin_rep_audio+audio, format="mp3")
				play(sound)
				print(transcript, audio)
	return



# if __name__ == "__main__":
	
	# print(sec2hms([2876.5379818594106]))
	# list_hms = ['00:59:47', '00:59:50'] # 00:39:52
	# # print(cumul_hms(list_hms))
	# tup_hms = ['00:19:58', '00:20:09']
	# print(diff_hms(tup_hms))

	# chemin_fichier = "../output/debat_entier/europeennes_europe1/"
    # nom_fichier = "europeennes_europe1.txt"

	# d = cumul_delta_borne_end_start(chemin_fichier, nom_fichier)
	# print(d)
	
	# print(delta_secondes((8388.169365079366, 8388.173832199547)))