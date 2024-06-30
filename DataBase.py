"""Programme de récupération et traitement des bases de données utilisées"""

from opensky_api import OpenSkyApi
import pandas as pd


def vol_aeroport(aeroport, debut, fin):
    """
    Utilisation de l'API de OpenSky pour récupérer et stocker dans une data frame les informations suivantes :

    | -'callsign' : Numéro donné à l'appareil par la compagnie aérienne
    | -'estArrivalAirport' : Code de l'aéroport d'arrivée
    | -'estDepartureAirport' : Code de l'aéroport de départ
    | -'icao24' : Numéro unique donné à l'appareil par l'OACI
    | -'firstSeen' : temps en UNIX pour laquelle l'avion a été vu la première fois
    | -'lastSeen' : temps en UNIX pour laquelle l'avion a été vu la dernière fois

    :param str aeroport: code OACI de l'aéroport en question
    :param int debut: début de l'intervalle de temps pour récupérer les vols en temps Unix
    :param int fin: fin de l'intervalle de temps pour récupérer les vols en temps Unix

    :return: DataFrame contenant les données des vols de départ ou arrivée 'aéroport'. De la forme :
     ['callsign','estArrivalAirport', 'estDepartureAirport', 'icao24', 'firstSeen', 'lastSeen']
    :rtype: DataFrame
    """
    api = OpenSkyApi()  # Création de l'instance api
    data_depart = api.get_departures_by_airport(aeroport, debut, fin)  # méthode pour récupérer tous les vols ayant
    #                                                                    comme aéroport de départ 'aéroport' durant
    #                                                                    la période début-fin
    data_arrivee = api.get_arrivals_by_airport(aeroport, debut, fin)  # même méthode, mais pour les aéroports d'arrivés
    flights_data_depart = []  # Liste dans laquelle est stockées les données des vols en provenance de 'aeroport'
    flights_data_arrivee = []  # De même pour les arrivées
    for flight in data_depart:  # Pour chaque vol renvoyé par l'api, récupère les informations nécessaires
        flight_info = {
            'callsign': flight.callsign,
            'estArrivalAirport': flight.estArrivalAirport,
            'estDepartureAirport': flight.estDepartureAirport,
            'icao24': flight.icao24,
            'firstSeen': flight.firstSeen,
            'lastSeen': flight.lastSeen,
        }
        flights_data_depart.append(flight_info)

    for flight in data_arrivee:
        flight_info = {
            'callsign': flight.callsign,
            'estArrivalAirport': flight.estArrivalAirport,
            'estDepartureAirport': flight.estDepartureAirport,
            'icao24': flight.icao24,
            'firstSeen': flight.firstSeen,
            'lastSeen': flight.lastSeen,
        }
        flights_data_arrivee.append(flight_info)

    # stocker les données récupérées dans une DataFrame
    col_names = ['callsign', 'estArrivalAirport', 'estDepartureAirport', 'icao24', 'firstSeen', 'lastSeen']
    flight_depart_df = pd.DataFrame(flights_data_depart, columns=col_names)  # Dataframe contenant les informations sur
    #                                                                          les vols ayant comme départ 'aeroport'
    flight_arrivee_df = pd.DataFrame(flights_data_arrivee, columns=col_names)  # De même pours les vols à destination de
    #                                                                            'aeroport'
    flight_df = pd.concat([flight_depart_df, flight_arrivee_df], ignore_index=True)  # Concaténation en une seule
    #                                                                                      dataframe
    return flight_df


def FAA(DF):
    """
    Fonction comparant croisant la data frame en entrée avec la base de donnée de la FAA.
    Cela permet de stocker uniquement les avions immatriculés aux États-Unis.

    Utilisation des bases de données :

    | -MASTER.csv (fournie par la FAA) : contient le numéro oaci de tous les appareils immatriculés aux États-Unis, leur
     code ainsi que le code de leur moteur
    | -ACFTREF.csv (fournie par la FAA) : contient le code des avions et leur modèle correspondant
    | -ENGINE.csv (fournie par la FAA) : contient le code des moteurs et leur modèle correspondant

    :param DF: DataFrame contenant au moins une colonne 'oaci24'
    :returns: DataFrame comportant les données des avions immatriculés aux États-Unis. 4 colonnes sont ajoutées par
     rapport à la data frame en entrée :

     | -index : ajout d'un index unique à chaque vol (de 1 à la taille du DataFrame)
     | -code : code de l'avion (donné par la FAA)
     | -model : nom du modèle exact de l'appareil
     | -modelReduit : nom du modèle réduit aux 4 premiers caractères pour seulement identifier la famille de l'appareil

    :rtype: DataFrame

    Un fichier 'flights_data.csv' est également sauvegardé. Il représente la base de donnée persistance à chaque requête
    """

    """Base de donnee master"""
    FAA_df = pd.read_csv('BaseDonnees/FAA/MASTER.csv', sep=',', encoding='utf-8', low_memory=False,
                         usecols=[2, 3, 33])  # Lecture des colonnes 'MFR MDL CODE', 'ENG MFR MDL' et 'MODE S CODE HEX'
    FAA_df.rename(columns={'MODE S CODE HEX': 'icao24'}, inplace=True)  # Changement de nom de 'MODE S CODE HEX' en
    #                                                                     'icao24'
    FAA_df.rename(columns={'MFR MDL CODE': 'codeModel'}, inplace=True)
    FAA_df.rename(columns={'ENG MFR MDL': 'codeEngine'}, inplace=True)
    FAA_df['icao24'] = FAA_df['icao24'].str.strip()  # Suppression des '' inutiles
    DF['icao24'] = DF['icao24'].str.upper()  # Les lettres minuscules deviennent majuscules
    merged_df = pd.merge(DF, FAA_df, on='icao24')  # Fusion de la base de donnée d'entrée avec celle de la FAA. Seuls
    #                                                 ayant un numéro oaci24 enregistré aux US sont gardés
    """Base de donnee modele"""
    model_df = pd.read_csv('BaseDonnees/FAA/ACFTREF.csv', sep=',', encoding='utf-8', low_memory=False,
                           usecols=[0, 2, 7])  # Lecture des colones 'CODE' et 'MODEL'
    model_df.rename(columns={'NO-ENG': 'numberEngine'}, inplace=True)
    model_df.rename(columns={'CODE': 'codeModel'}, inplace=True)
    model_df.rename(columns={'MODEL': 'model'}, inplace=True)
    merged_df = pd.merge(merged_df, model_df, on='codeModel')  # Fusion de la base de donnée précédemment fusionnée avec
    #                                                       celle contenant les modèles des avions associés à leur
    #                                                       'code'
    merged_df['model'] = merged_df['model'].str.strip()
    merged_df['modelReduit'] = merged_df['model'].str[:4]  # Nouvelle colonne 'modelReduit contenant les 4 premiers
    #                                                        caractères de la colonne 'model'
    merged_df['modelReduit'] = merged_df['modelReduit'].str.replace('-', '')  # Suppression des '-'

    """Base de donnee engine"""
    engine_df = pd.read_csv('BaseDonnees/FAA/ENGINE.csv', sep=',', encoding='utf-8', usecols=[0, 2],
                            dtype={'CODE': str})  # Lecture des colonnes 'codeEngine' et 'modelEngine'
    #                                                     Ajout du dtype pour conserver les 0 au début du CODE sinon
    #                                                     00401 devient 401
    engine_df.rename(columns={'CODE': 'codeEngine'}, inplace=True)
    engine_df.rename(columns={'MODEL': 'modelEngine'}, inplace=True)

    # merged_df['codeEngine'] = merged_df['codeEngine'].astype(str)   # Changement en str des colonnes 'codeEngine' pour
    # engine_df['codeEngine'] = engine_df['codeEngine'].astype(str)   # pouvoir les comparer et fusionner
    merged_df = pd.merge(merged_df, engine_df, on='codeEngine', how='left')  # Association de chaque avion à son moteur
    return merged_df


def airplane_traj(index):
    """
    Permet d'obtenir grâce à l'api d'OpenSky le trajet d'un certain vol du fichier 'flights_data.csv' identifié par son
    index. La trajectoire est caractérisée par :

    | -temps : int - temps du waypoint donné en UNIX
    | -latitude : float - latitude géographique en dixième de degré
    | -longitude : float - longitude géographique en dixième de degré
    | -altitude barométrique : float - altitude barométrique en mètre
    | -cap vrai : float - cap vrai de l'avion en dixième de degré (nord = 0°)
    | -état : bool - état au sol de l'avion : True → au sol, False → pas au sol

    :param index: Index de l'avion dans le fichier 'flights_data.csv'

    :return: Liste de liste, de la forme : ['temps', 'latitude', 'longitude', 'altitude barométrique', 'cap vrai', 'état
        ']

    :rtype: Liste Python
    """
    traj_df = pd.read_csv('flights_data.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[0, 4, 5])
    icao24 = traj_df.loc[index, 'icao24'].lower()
    t = traj_df.loc[index, 'firstSeen']
    api = OpenSkyApi()
    data = api.get_track_by_aircraft(icao24, t)
    return data.path


def compagnie(DF):
    """
    Fonction qui associe à chaque vol du DataFrame en entrée sa compagnie. La base de donnée 'callsign.csv' (créée pour
    le projet) est utilisée, elle fait le lien entre les 3 premières lettres du callsign à la compagnie.

    :param DF: DataFrame contenant au moins le callsign des vols
    :return: DataFrame d'entrée avec une nouvelle colonne 'compagnie'
    :rtype: DataFrame
    """
    compagnie_df = pd.read_csv('BaseDonnees/callsign.csv', sep=',', encoding='utf-8')
    DF['callsign3'] = DF['callsign'].str[:3]
    DF = pd.merge(DF, compagnie_df, left_on='callsign3', right_on='callsign', how='left')
    DF = DF.drop(columns=['callsign3', 'callsign_y'])
    DF.rename(columns={'callsign_x': 'callsign'}, inplace=True)
    DF['compagnie'] = DF['compagnie'].fillna('Inconnue')

    return DF


def easa(DF):
    """
    Fonction qui associe à chaque vol du DataFrame en entrée le numéro UID de l'easa de son moteur. La base de donnée
    'easaEmission.csv' (fournie par l'EASA) est utilisée. Elle contient les différentes émissions d'un grand nombre de
    moteurs.

    :param DF: DataFrame contenant au moins des moteurs
    :return: DataFrame d'entrée avec une nouvelle colonne 'uid'
    :rtype: DataFrame
    """
    easa_df = pd.read_csv('BaseDonnees/EASA/nvPM Emissions.csv', sep=',', encoding='utf-8',
                          usecols=[0, 3])  # Lecture des colonnes 'UID No' et 'MODEL'

    easa_df.rename(columns={'Engine Identification': 'modelEngine'}, inplace=True)
    easa_df.rename(columns={'UID No': 'uid'}, inplace=True)
    easa_df = easa_df.drop_duplicates(subset=['modelEngine'])   # Suppression des doublons dans la colonne 'modelEngine'

    DF['modelEngine'] = DF['modelEngine'].str.strip()

    DF = pd.merge(DF, easa_df, on='modelEngine')
    return DF


def emission(index):
    """
    Fonction fournissant les caractéristiques données par l'EASA du moteur du vol à l'indice 'index' du DataFrame
    d'entrée.

    :param int index: Index du vol en question
    :return: DataFrame d'une ligne contenant les caractéristiques du moteur du vol en question
    """
    emission_df = pd.read_csv('BaseDonnees/EASA/Gaseous Emissions and Smoke.csv', sep=',', encoding='utf-8')
    flights_df = pd.read_csv('flights_data.csv', sep=',', encoding='utf-8')
    uid = flights_df.loc[index, 'uid']
    ligne = emission_df[emission_df['UID No'] == uid]
    return ligne


def sortie(aeroport, debut, fin):
    """
    Fonction qui enchaine dans le bon ordre toutes fonctions de traitements des bases de données.

    :param str aeroport: Code OACI de l'aéroport en question
    :param int debut: Début de l'intervalle de temps pour récupérer les vols en temps Unix
    :param int fin: Fin de l'intervalle de temps pour récupérer les vols en temps Unix
    :return: DataFrame contenant toutes les informations sur les vols provenant et en direction de 'aeroport' dans
     l'intervalle de temps [debut, fin]
    """
    DF = easa(FAA(compagnie(vol_aeroport(aeroport, debut, fin))))  # Ajout de la colonne index
    DF.insert(0, 'index', range(1, len(DF) + 1))
    DF.to_csv('flights_data.csv', index=False)  # Sauvegarde le DataFrame dans un fichier CSV
    return DF
