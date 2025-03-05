from pydub import AudioSegment
from pydub.playback import play
import glob
from glob import glob
import argparse

def num_fichier(chemin_fichier: str):
	""" Retourne au format int le numéro au format string au début du nom de fichier """
	return int(chemin_fichier.split('/')[-1].split('_')[0])


def read_audiofile(chemin_rep_transcript: str, chemin_rep_audio: str):
	""" Ouvre simultanément :
	 - le fichier de la phrase négative transcrite, l'affiche sur le Terminal
	 - le fichier du segment audio correspondant et le lit
	""" 
	list_transcripts = glob(chemin_rep_transcript + '/*.txt')
	list_transcripts.sort(key=num_fichier)
	# print(list_transcripts)
	list_audio = glob(chemin_rep_audio + '/*.mp3')
	list_audio.sort(key=num_fichier)
	# print(list_audio)
	
	# cpteur = 0
	
	while True:
		try:
			i = input("\nEntrez le n° de la phrase négative à écouter\n\
			 		'Enter' pour écouter les phrases à partir du début et les suivantes.\n\
			 		'q' + 'Enter' pour quitter : ")
			if i.isdigit():
				cpteur = int(i)
				print(list_transcripts[cpteur-1])
				with open(chemin_rep_transcript+list_transcripts[cpteur-1].split('/')[-1]) as f:
					print(f"Phrase négative n° {cpteur} :\n")
					print(f.read()+"\n\n")
					sound = AudioSegment.from_file(chemin_rep_audio+list_audio[cpteur-1].split('/')[-1], format="mp3")
					play(sound)

					s = input("Taper sur 'r' + entrée pour répéter, 'c' + entrée pour les phrases suivantes, 'q' + entrée pour sortir : ")
					if s == "r":
						play(sound) # si je met pass ou continue reste sur le play(sound) de la phrase courante
					elif s == "c": # on repart dans le fichier à niveau de la phrase suivante
						cpteur = cpteur+1
						print(cpteur)
						for transcript, audio in zip(list_transcripts[cpteur-1:], list_audio[cpteur-1:]):
							with open(transcript) as f2:
								print(f"Phrase négative n° {cpteur} :\n")
								print(f2.read()+"\n\n")
								sound = AudioSegment.from_file(audio, format="mp3")
								play(sound)
								# print(transcript, audio)
								s = input("'r' + 'Enter' pour répéter, 'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
								if s == "r":
									play(sound)
									continue
								elif s == "q":
									break
								else:
									cpteur += 1
									continue
					elif s == "q":
						break
			elif i == "q":
						break
			else:
				cpteur = 0
				for transcript, audio in zip(list_transcripts, list_audio):
					with open(transcript) as f:
						cpteur += 1
						print(f"Phrase négative n° {cpteur} :\n")
						print(f.read()+"\n\n")
						sound = AudioSegment.from_file(audio, format="mp3")
						play(sound)
						s = input("'r' + 'Enter' pour répéter, 'Enter' pour les phrases suivantes, q + 'Enter' pour sortir : ")
						if s == "r":
							play(sound)
							break
						elif s == "q":
							break
						else:
							continue
		except Exception as e:
			print(f"Error playing sound: {e}")
	
	return

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="1er argument : nom du débat")
	parser.add_argument("nom_debat", help="nom du débat transcrit")
	args = parser.parse_args()
	nom_debat = args.nom_debat

	chemin_transcript = f"../output/ph_neg/{nom_debat}/{nom_debat}_txt/"
	chemin_audio = f"../output/ph_neg/{nom_debat}/{nom_debat}_audio/"
	read_audiofile(chemin_transcript, chemin_audio)