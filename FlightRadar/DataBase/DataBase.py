"""Programme de récupération et traitement des bases de données utilisées"""

from FlightRadar.DataBase.opensky_api import OpenSkyApi
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


def faa(df):
    """
    Fonction comparant croisant la data frame en entrée avec la base de donnée de la FAA.
    Cela permet de stocker uniquement les avions immatriculés aux États-Unis.

    Utilisation des bases de données :

    | -MASTER.csv (fournie par la FAA) : contient le numéro oaci de tous les appareils immatriculés aux États-Unis, leur
     code ainsi que le code de leur moteur
    | -ACFTREF.csv (fournie par la FAA) : contient le code des avions et leur modèle correspondant
    | -ENGINE.csv (fournie par la FAA) : contient le code des moteurs et leur modèle correspondant

    :param df: DataFrame contenant au moins une colonne 'oaci24'
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
    faa_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/FAA/MASTER.csv', sep=',', encoding='utf-8', low_memory=False,
                         usecols=[2, 3, 33])  # Lecture des colonnes 'MFR MDL CODE', 'ENG MFR MDL' et 'MODE S CODE HEX'
    faa_df.rename(columns={'MODE S CODE HEX': 'icao24'}, inplace=True)  # Changement de nom de 'MODE S CODE HEX' en
    #                                                                     'icao24'
    faa_df.rename(columns={'MFR MDL CODE': 'codeModel'}, inplace=True)
    faa_df.rename(columns={'ENG MFR MDL': 'codeEngine'}, inplace=True)
    faa_df['icao24'] = faa_df['icao24'].str.strip()  # Suppression des '' inutiles
    df['icao24'] = df['icao24'].str.upper()  # Les lettres minuscules deviennent majuscules
    merged_df = pd.merge(df, faa_df, on='icao24')  # Fusion de la base de donnée d'entrée avec celle de la FAA. Seuls
    #                                                 ayant un numéro oaci24 enregistré aux US sont gardés
    """Base de donnee modele"""
    model_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/FAA/ACFTREF.csv', sep=',', encoding='utf-8', low_memory=False,
                           usecols=[0, 2, 7])  # Lecture des colones 'CODE' et 'MODEL'
    model_df.rename(columns={'NO-ENG': 'numberEngine'}, inplace=True)
    model_df.rename(columns={'CODE': 'codeModel'}, inplace=True)
    model_df.rename(columns={'MODEL': 'model'}, inplace=True)
    merged_df = pd.merge(merged_df, model_df, on='codeModel')  # Fusion de la base de donnée précédemment fusionnée avec
    #                                                       celle contenant les modèles des avions associés à leur
    #                                                       'code'
    merged_df['model'] = merged_df['model'].str.strip()
    merged_df['modelReduit'] = merged_df['model'].str[:4].str.strip()  # Nouvelle colonne 'modelReduit contenant les 4 premiers
    #                                                        caractères de la colonne 'model'
    merged_df['modelReduit'] = merged_df['modelReduit'].str.replace('-', '')  # Suppression des '-'

    """Base de donnee engine"""
    engine_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/FAA/ENGINE.csv', sep=',', encoding='utf-8', usecols=[0, 2],
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
    traj_df = pd.read_csv('FlightRadar/DataBase/flights_data.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[0, 4, 5])
    icao24 = traj_df.loc[index, 'icao24'].lower()
    t = traj_df.loc[index, 'firstSeen']
    api = OpenSkyApi()
    data = api.get_track_by_aircraft(icao24, t)
    return data.path


def compagnie(df):
    """
    Fonction qui associe à chaque vol du DataFrame en entrée sa compagnie. La base de donnée 'callsign.csv' (créée pour
    le projet) est utilisée, elle fait le lien entre les 3 premières lettres du callsign à la compagnie.

    :param df: DataFrame contenant au moins le callsign des vols
    :return: DataFrame d'entrée avec une nouvelle colonne 'compagnie'
    :rtype: DataFrame
    """
    compagnie_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/callsign.csv', sep=',', encoding='utf-8')
    df['callsign3'] = df['callsign'].str[:3]
    df = pd.merge(df, compagnie_df, left_on='callsign3', right_on='callsign', how='left')
    df = df.drop(columns=['callsign3', 'callsign_y'])
    df.rename(columns={'callsign_x': 'callsign'}, inplace=True)
    df['compagnie'] = df['compagnie'].fillna('Inconnue')

    return df


def easa(df):
    """
    Fonction qui associe à chaque vol du DataFrame en entrée le numéro UID de l'easa de son moteur. La base de donnée
    'easaEmission.csv' (fournie par l'EASA) est utilisée. Elle contient les différentes émissions d'un grand nombre de
    moteurs.

    :param df: DataFrame contenant au moins des moteurs
    :return: DataFrame d'entrée avec une nouvelle colonne 'uid'
    :rtype: DataFrame
    """
    easa_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/EASA/Gaseous Emissions and Smoke.csv', sep=',', encoding='utf-8',
                          usecols=[0, 3])  # Lecture des colonnes 'UID No' et 'MODEL'

    easa_df.rename(columns={'Engine Identification': 'modelEngine'}, inplace=True)
    easa_df.rename(columns={'UID No': 'uid'}, inplace=True)
    easa_df = easa_df.drop_duplicates(subset=['modelEngine'])   # Suppression des doublons dans la colonne 'modelEngine'

    df['modelEngine'] = df['modelEngine'].str.strip()

    df = pd.merge(df, easa_df, on='modelEngine')
    return df


def engine_emission(uid):
    """
    Fonction fournissant les caractéristiques données par l'EASA du moteur du vol à l'indice 'index' du DataFrame
    d'entrée.

    :param str uid: Numéro uid unique au moteur
    :return: DataFrame d'une ligne contenant les caractéristiques du moteur du vol en question
    """
    emission_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/EASA/Gaseous Emissions and Smoke.csv', sep=',', encoding='utf-8')
    ligne = emission_df[emission_df['UID No'] == uid]
    return ligne


def similar_engines(uid):
    poussee = float(engine_emission(uid)['Rated Thrust (kN)'].iloc[0])

    easa_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/EASA/Gaseous Emissions and Smoke.csv', sep=',', encoding='utf-8', usecols=['UID No', 'Engine Identification', 'Rated Thrust (kN)', 'Fuel Flow T/O (kg/sec)', 'Fuel LTO Cycle (kg)  '])
    easa_df['Rated Thrust (kN)'] = easa_df['Rated Thrust (kN)'].astype(float)
    # Calculer la différence absolue entre la poussée de chaque moteur et la valeur cible
    easa_df['difference'] = abs(easa_df['Rated Thrust (kN)'] - poussee)
    engine_id_to_remove = easa_df.loc[easa_df['UID No'] == uid, 'Engine Identification'].values[0]
    easa_df = easa_df[easa_df['Engine Identification'] != engine_id_to_remove]
    easa_df = easa_df.dropna(subset=["Fuel Flow T/O (kg/sec)"])
    easa_df = easa_df.dropna(subset=["Fuel LTO Cycle (kg)  "])

    # Trier les moteurs par cette différence
    easa_df = easa_df.sort_values('difference')
    # Filtrer pour obtenir les moteurs de marques différentes
    moteurs_proches = []
    marques = set()
    for index, row in easa_df.iterrows():
        marque = row['Engine Identification'][:2]
        if marque not in marques:
            moteurs_proches.append([row['UID No'], row['Engine Identification']])
            marques.add(marque)
        if len(moteurs_proches) == 5:
            break

    # Convertir la liste de résultats en DataFrame
    moteurs_proches_df = pd.DataFrame(moteurs_proches, columns=['uid', 'modelEngine'])

    return moteurs_proches_df


def sortie(aeroport, debut, fin):
    """
    Fonction qui enchaine dans le bon ordre toutes fonctions de traitements des bases de données.

    :param str aeroport: Code OACI de l'aéroport en question
    :param int debut: Début de l'intervalle de temps pour récupérer les vols en temps Unix
    :param int fin: Fin de l'intervalle de temps pour récupérer les vols en temps Unix
    :return: DataFrame contenant toutes les informations sur les vols provenant et en direction de 'aeroport' dans
     l'intervalle de temps [debut, fin]
    """
    df = easa(faa(compagnie(vol_aeroport(aeroport, debut, fin))))  # Ajout de la colonne index
    df.insert(0, 'index', range(1, len(df) + 1))
    df.to_csv('FlightRadar/DataBase/flights_data.csv', index=False)  # Sauvegarde le DataFrame dans un fichier CSV
    return df


def aircraft_emission(reduced_model):
    """
    Fonction fournissant les caractéristiques d'un modèle d'avion reduced_model, nécessaires pour calculer les émissions
    CO2 par passager.

    :param int reduced_model: Abbréviation du modèle de l'avion
    :return: DataFrame d'une ligne contenant les caractéristiques de l'avion du vol en question
    """
    emission_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/aircraft_parameters.csv', sep=';', encoding='utf-8')
    return emission_df[emission_df['modelReduit'] == reduced_model].reset_index(drop=True)


def model_is_present(reduced_model):
    """
    Vérifie si un modèle d'avion reduced_model est présent dans la base de données.

    :param int reduced_model: Abbréviation du modèle de l'avion.
    :return: True si le modèle est présent, False sinon.
    :rtype: bool
    """
    emission_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/aircraft_parameters.csv', sep=';', encoding='utf-8')
    if reduced_model in emission_df["modelReduit"].values:
        return True
    return False


def similar_models(reduced_model):
    """
    Trouve des modèles d'avion similaires à un modèle d'avion reduced_model donné.

    Les modèles similaires sont ceux qui ont le même facteur de classe de sièges (CW) et une capacité de sièges (S)
    supérieure ou égale à celle du modèle réduit, à l'exception du modèle réduit lui-même.

    :param int reduced_model: Abbréviation du modèle de l'avion.
    :return: Liste des abréviations des modèles d'avion similaires.
    :rtype: list
    """
    if model_is_present(reduced_model):
        emission_df = pd.read_csv('FlightRadar/DataBase/BaseDonnees/aircraft_parameters.csv', sep=';', encoding='utf-8')
        emission_df.drop(index=[0, 1], inplace=True)
        reduced_model_index = emission_df.loc[emission_df["modelReduit"] == reduced_model].index[0]
        emission_df = emission_df[emission_df["CW"] == emission_df["CW"][reduced_model_index]]
        emission_df = emission_df[emission_df["S"] >= emission_df["S"][reduced_model_index]]
        emission_df.drop(index=reduced_model_index, inplace=True)
        return emission_df["modelReduit"].values.tolist()[:5]
    return []
