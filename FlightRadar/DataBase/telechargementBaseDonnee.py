"""Programme permettant de télécharger les bases de données en ligne. Le code a été généré via chat GPT car il nécessite
la comprehension des "certificats" que nous n'avons eu le temps d'apprendre"""
import urllib.request
import ssl
import os
import time
import zipfile
import certifi
import pandas as pd


# FAA("https://registry.faa.gov/database/ReleasableAircraft.zip",'BaseDonnees/FAA',
    #               ['MASTER.txt', 'ENGINE.txt', 'ACFTREF.txt'])
def base_de_donnees_FAA():
    """Télécharge la base de donnée de la FAA et l'enregistre dans le dossier FAA"""
    # URL du fichier à télécharger
    url = "https://registry.faa.gov/database/ReleasableAircraft.zip"

    dossier_de_depot = 'FlightRadar/DataBase/BaseDonnees/FAA'
    # Vérifiez si le répertoire existe déjà
    if not os.path.exists(dossier_de_depot):
        os.makedirs(dossier_de_depot, exist_ok=True)
    else:
        print(f"Le répertoire {dossier_de_depot} existe déjà. Arrêt du téléchargement.")
        return

    # Chemin complet du fichier téléchargé
    destination_file_path = os.path.join(dossier_de_depot, os.path.basename(url))

    # Créez un contexte SSL en utilisant les certificats de certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Fonction pour télécharger un fichier avec des tentatives de réessai
    def download_file(url, destination_file_path, ssl_context, max_retries=5):
        attempt = 0
        while attempt < max_retries:
            try:
                print(f"Tentative {attempt + 1} de téléchargement...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response, open(destination_file_path, 'wb') as out_file:
                    file_size = int(response.getheader('Content-Length'))
                    downloaded = 0
                    buffer_size = 1024 * 1024  # 1MB
                    while True:
                        buffer = response.read(buffer_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        print(f"Téléchargé {downloaded} de {file_size} octets ({downloaded/file_size:.2%})")
                print(f"Le fichier a été téléchargé dans : {destination_file_path}")
                return
            except Exception as e:
                print(f"Une erreur est survenue lors de la tentative {attempt + 1} : {e}")
                attempt += 1
                time.sleep(5)  # Attendez 5 secondes avant de réessayer
        print("Échec du téléchargement après plusieurs tentatives.")

    # Télécharger le fichier avec des tentatives de réessai
    download_file(url, destination_file_path, ssl_context)

    # Spécifiez les fichiers à extraire
    fichiers_a_extraire = ['MASTER.txt', 'ENGINE.txt', 'ACFTREF.txt']  # Remplacez par les noms des fichiers dont vous avez besoin

    # Extraire et renommer les fichiers nécessaires
    print("Extraction et renommage des fichiers nécessaires du fichier ZIP...")
    try:
        with zipfile.ZipFile(destination_file_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file in fichiers_a_extraire:
                    zip_ref.extract(file, dossier_de_depot)
                    base_name = os.path.splitext(file)[0]
                    new_name = base_name + '.csv'
                    old_file_path = os.path.join(dossier_de_depot, file)
                    new_file_path = os.path.join(dossier_de_depot, new_name)
                    os.rename(old_file_path, new_file_path)
                    print(f"Extrait et renommé : {file} -> {new_name}")
                else:
                    print(f"Ignoré : {file}")
        print(f"Les fichiers nécessaires ont été extraits et renommés dans : {dossier_de_depot}")
        os.remove("BaseDonnees/FAA/ReleasableAircraft.zip")
        print("Le fichier Zip a été supprimé : BaseDonnees/FAA/ReleasableAircraft.zip")

    except Exception as e:
        print(f"Une erreur est survenue lors de l'extraction : {e}")





def base_de_donnees_EASA():
    """Télécharge la base de donnée de l'EASA et l'enregistre dans le dossier EASA"""
    # URL du fichier à télécharger
    url = 'https://www.easa.europa.eu/en/downloads/131424/en'

    # Répertoire de destination
    destination_directory = 'FlightRadar/DataBase/BaseDonnees/EASA'

    # Vérifiez si le répertoire existe déjà
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory, exist_ok=True)
    else:
        print(f"Le répertoire {destination_directory} existe déjà. Arrêt du téléchargement.")
        return

    # Chemin complet du fichier téléchargé
    destination_file_path = os.path.join(destination_directory, 'edb-emissions-databank_draft_v29B__web_.xlsx')

    # Créer un contexte SSL en utilisant les certificats de certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        # Ouvrir une connexion avec l'URL en utilisant le contexte SSL
        with urllib.request.urlopen(url, context=ssl_context) as response, open(destination_file_path, 'wb') as out_file:
            # Lire les données depuis la réponse et les écrire dans le fichier local
            out_file.write(response.read())

        print(f"Le fichier a été téléchargé avec succès dans : {destination_file_path}")

        # Charger le fichier Excel en utilisant pandas
        xl = pd.ExcelFile(destination_file_path)

        sheet_names = ["Gaseous Emissions and Smoke", "nvPM Emissions"]
        for sheet_name in sheet_names:
            # Vérifier si la feuille spécifiée existe
            if sheet_name in xl.sheet_names:
                # Charger la feuille spécifiée en tant que DataFrame
                df = xl.parse(sheet_name)

                # Chemin pour le fichier CSV de sortie
                csv_file_path = os.path.join(destination_directory, f"{sheet_name}.csv")

                # Enregistrer le DataFrame en tant que fichier CSV
                df.to_csv(csv_file_path, index=False)
                print(f"La feuille '{sheet_name}' a été enregistrée en CSV : {csv_file_path}")

            else:
                print(f"La feuille '{sheet_name}' n'existe pas dans le fichier Excel.")
            # Supprimer le fichier Excel une fois le CSV extrait
        os.remove(destination_file_path)
        print(f"Le fichier Excel a été supprimé : {destination_file_path}")

    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement : {e}")



