## Description de la chaîne de traitement
 Elle prend un fichier audio en entrée, le transcrit, puis extrait les phrases négatives de la transcription pour les présenter dans un tableur qui comporte, dans des colonnes distinctes :
 
 - le n° d'identification de la phrase
 - la position temporelle de la phrase dans le fichier audio du débat
 - la phrase transcrite corrigée à l'écoute
 
À partir de ce tableur de référence, on ajoutera d'autres caractéristiques associées à l'analyse de la phrase.

## Préparation des fichers audios
L'étape de préparation comporte des opérations manuelles : téléchargement et conversion des fichiers vidéos ou son, scission des fichiers en fichiers de 20 min.

Les fichiers audio lus en entrée de la chaîne de traitement sont au format .mp3 et à une fréquence d’échantillonnage de 44100 Hz.

Les choix du format .mp3, de la fréquence d'échantillonage et de la durée ne sont pas contraints par le modèle de transcription, ils ont été fixés suite à des essais avec le modèle de transcription.

## Chaîne de traitement
Du fichier audio jusqu'au fichier csv de phrases négatives, le traitement passe par trois modules. Les scripts sont lancés avec le nom du débat en argument à la ligne de commande.

<img title="Pipeline pour un débat" src="https://github.com/Aliwasan/stage_negation/blob/main/img/flow_pipeline.svg" alt="" align="center">

### Module de transcription
#### audiototranscript.py:

La fonction ***transcription()*** prend un nom de répertoire de fichiers audios charge le modèle whisper donné en argument et transcrit les fichiers audios du répertoire.

Elle retourne deux fichiers textes:
- un fichier de la transcription complète du répertoire audio
- un fichier avec la transcription du répertoire audio sous forme de segments (un par ligne) horodatée en secondes, par ex : 218.72 - 219.79999999999998:  – C'est faux, sortir des règles."

### Module d'extraction

#### make_data.py:
> La fonction ***concat_seg_horo()*** reconstitue les phrases.Elle lit le fichier de transcriptions ligne par ligne et concatène les segments de chaque ligne correspondant à un début, un milieu ou une fin de phrase en tenant compte des marqueurs de fin de phrase. Les horodadeurs des segments du début et de fin sont conservés.\
Retourne : une liste de tuples (horodateur, texte de la phrase).

> La fonction ***find_neg()*** détecte les phrases négatives à partir à p. d'une regex des mots négatifs, désambiguïse les occurrences de "pas", "plus" et "personne" grâce à l'étiquette Polarity=Neg de Spacy.\
Retourne :
- un fichier .json avec le n° phrase négative, l'horodateur en secondes et en hms, la phrase transcrite.
- une variable contenant un dataframe avec les mêmes informations.

> La fonction ***df_to_csv()*** prend un dataframe et retourne un fichier csv.

> La fonction ***horo_transcr_ph_neg()*** permet de corriger chaque transcription à partir de l'écoute. Elle convertit les horodateurs donnés au format sec au format millisecondes pour s'adapter à PyDub (https://github.com/jiaaro/pydub/blob/master/README.markdown) et segmente fichier audio en plusieurs fichiers audios.\
Retourne deux répertoires de fichiers parallèles, chaque fichier contient une phrase négative :
- son audio dans le répertoire audio
- sa transcription dans le répertoire txt.

#### read_audiofile_prompt.py

> La fonction ***read_audiofile()*** ouvre simultanément le fichier de la phrase négative transcrite qu'elle affiche sur le Terminal et le fichier du segment audio correspondant qu'elle lit. Elle ouvre un prompt permettant de corriger la transcription de la phrase.\
Elle retourne la liste des phrases corrigées.

> La fonction ***add_col_to_csv()*** prend la liste de phrases corrigées et l'insère dans la colonne "ph_corrigee" du csv de référence.

### Module d'annotation


