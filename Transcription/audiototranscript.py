import argparse
import os
import sys
import whisper
import json
import mutagen
from mutagen.mp3 import MP3
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utils'))        
import utils

def transcription(chemin_rep_audio:str, type_modele:str, chemin_fichier_transcrit:str, nom_debat:str):
    """ 
        https://github.com/openai/whisper/blob/main/README.md
        Prend un nom de répertoire de fichiers audios 
        charge le modèle whisper donné et transcrit les fichiers audios du répertoire
        retourne un fichier texte avec la transcription sous forme de segments (un par ligne) horodatés en secondes
        ex : 218.72 - 219.79999999999998:  – C'est faux, sortir des règles.
        Ajoute la durée du fichier en secondes, récupérée avec mutagen, à la première borne (0.0) du fichier suivant
        pour respecter la continuité du marquage temporel à l'échelle du débat.
    """
    try:
        os.mkdir(f"{chemin_fichier_transcrit}{nom_debat}")
        print(f"Directory '{nom_debat}' created successfully.")
    except FileExistsError:
        print(f"Directory '{nom_debat}' already exists.")
        pass
    
    print("Chargement du modèle")
    model = whisper.load_model(type_modele)
    list_audiofiles = utils.liste_ord_rep(chemin_rep_audio, '.mp3')
    
    
    with open(chemin_fichier_transcrit + nom_debat + "/" + nom_debat + ".txt", 'w', encoding='utf-8') as file_transcript, open(chemin_fichier_transcrit + nom_debat + "/" + nom_debat + "_texte_entier.txt", 'w', encoding='utf-8') as file_total_transcript:
        cpteur_fichier = 0
        end_time = 0.0
        duree_fichier = 0.0
        for f in list_audiofiles:
            cpteur_fichier += 1
            print(f"fichier n° :{cpteur_fichier}")
            print(f"Transcription de {f} commencée")
            transcript = model.transcribe(chemin_rep_audio + f, language="french")
            print(f"Transcription de {f} terminée")
            print(f"Taille du fichier en nbre de segments audio : {len(transcript['segments'])}")

            # dump des données
            transcript_dump = json.dumps(transcript, indent = 2, ensure_ascii = False)
            print(transcript_dump)

            # # récupération du texte_entier
            file_total_transcript.write(transcript['text'])

            # récupération des segments avec horo
            for dico_segment in transcript["segments"]:
                print(dico_segment)
                if cpteur_fichier == 1:
                    start_time = dico_segment['start']
                    end_time = dico_segment['end']
                    file_transcript.write(f"{start_time} - {end_time}: {dico_segment['text']}\n")
                else:
                    # print(f"ajout de la durée du fichier précédent : {duree_fichier}")
                    start_time = duree_fichier + dico_segment['start']
                    end_time = start_time + (dico_segment['end'] - dico_segment['start'])
                    file_transcript.write(f"{start_time} - {end_time}: {dico_segment['text']}\n")
            
            audio = MP3(chemin_rep_audio + f)
            duree_fichier += audio.info.length
            print(f"end_time à la fin du fichier n° {cpteur_fichier} : {end_time}")
            print(f"duree_fichier {cpteur_fichier} : {duree_fichier}")
    return


if __name__ == "__main__":
    
    type_modele = "turbo"
    
    parser = argparse.ArgumentParser(description = "1er argument : nom du débat")
    parser.add_argument("nom_debat", help = "nom du débat transcrit")
    args = parser.parse_args()
    nom_debat = args.nom_debat
    
    chemin_fichier_transcrit = "../output/debat_entier/"
    nom_rep = f"../audio/{nom_debat}/"


    startTime = datetime.datetime.now()

    transcription(nom_rep, type_modele, chemin_fichier_transcrit, nom_debat)

    endTime = datetime.datetime.now()

    print(f"Temps traitement transcription : {endTime - startTime}")