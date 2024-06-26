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
    flight_df = pd.concat([flight_depart_df, flight_arrivee_df],ignore_index=True)  # Concaténation en une seule
    #                                                                                      dataframe
    return flight_df


def FAA(DF):
    """
    Fonction comparant croisant la data frame en entrée avec la base de donnée de la FAA.
    Cela permet de stocker uniquement les avions immatriculés aux États-Unis et de leur associé leur modèle.
    Utilisation des bases de données :

    | -master.csv (fournie par la FAA) : contient le numéro oaci de tous les appareils immatriculés aux États-Unis ainsi que leur code
    | -model.csv (fournie par la FAA) : contient le code des avions et leur modèle

    :param DF: DataFrame contenant au moins une colonne 'oaci24'
    :returns: DataFrame comportant les données des avions immatriculés aux États-Unis. 4 colonnes sont ajoutés par rapport à la data frame en entrée :

     | -index : ajout d'un index unique à chaque vol (de 1 à la taille du DataFrame)
     | -code : code de l'avion (donné par la FAA)
     | -model : nom du modèle exact de l'appareil
     | -modelReduit : nom du modèle réduit aux 4 premiers caractères pour seulement identifier la famille de l'appareil

    :rtype: DataFrame

    Un fichier 'flights_data.csv' est également sauvegardé. Il représente la base de donnée persistance à chaque requête
    """

    """Base de donnee master"""
    FAA_df = pd.read_csv('BaseDonnees/FAA/master.csv', sep=',', encoding='utf-8', low_memory=False,
                         usecols=[2, 33])  # Lecture des colonnes 'MODE S CODE HEX' et 'MFR MDL CODE'
    FAA_df.rename(columns={'MODE S CODE HEX': 'icao24'}, inplace=True)  # Changement de nom de 'MODE S CODE HEX' à
    #                                                                     'icao24'
    FAA_df.rename(columns={'MFR MDL CODE': 'CODE'}, inplace=True)  # Changement de nom de 'MFR MDL CODE' à 'CODE'
    FAA_df['icao24'] = FAA_df['icao24'].str.strip()  # Suppression des '' inutiles.

    """Base de donnee modele"""
    model_df = pd.read_csv('BaseDonnees/FAA/modele.csv', sep=',', encoding='utf-8', low_memory=False,
                           usecols=[0, 2])  # Lecture des colones 'CODE' et 'MODEL'

    DF['icao24'] = DF['icao24'].str.upper()  # Les lettres minuscules deviennent majuscules
    merged_df = pd.merge(DF, FAA_df, on='icao24')   # Fusion de la base de donnée d'entrée avec celle de la FAA. Seuls
    #                                                 ayant un numéro oaci24 enregistré aux US sont gardés
    merged_df = pd.merge(merged_df, model_df, on='CODE')  # Fusion de la base de donnée précédemment fusionnée avec
    #                                                       celle contenant les modèles des avions associés à leur
    #                                                       'code'

    merged_df.rename(columns={'CODE': 'code'}, inplace=True)  # Changement de nom de 'CODE' à 'code'
    merged_df.rename(columns={'MODEL': 'model'}, inplace=True)  # Changement de nom de 'MODEL' à 'model'

    merged_df['modelReduit'] = merged_df['model'].str[:4]  # Nouvelle colonne 'modelReduit contenant les 4 premiers
    #                                                        caractères de la colonne 'model'
    merged_df['modelReduit'] = merged_df['modelReduit'].str.replace('-', '')  # Suppression des '-'

    merged_df.insert(0, 'index', range(1, len(merged_df) + 1))  # Ajout de la colonne index

    merged_df.to_csv('flights_data.csv', index=False)  # Sauvegarde le DataFrame dans un fichier CSV
    return merged_df


def airplane_traj(index):
    traj_df = pd.read_csv('flights_data.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[0, 4, 5])
    icao24 = traj_df.loc[index, 'icao24'].lower()
    t = traj_df.loc[index, 'firstSeen']
    api = OpenSkyApi()
    data = api.get_track_by_aircraft(icao24, t)
    return data.path


def compagnie(DF):
    compagnie_df = pd.read_csv('BaseDonnees/callsign.csv', sep=',', encoding='utf-8')
    DF['callsign3'] = DF['callsign'].str[:3]
    DF = pd.merge(DF, compagnie_df, left_on='callsign3', right_on='callsign', how='left')
    DF = DF.drop(columns=['callsign3', 'callsign_y'])
    DF.rename(columns={'callsign_x': 'callsign'}, inplace=True)
    DF['compagnie'] = DF['compagnie'].fillna('Inconnue')
    return DF


def sortie(aeroport, temps_debut, temps_fin):
    return FAA(compagnie(vol_aeroport(aeroport, temps_debut, temps_fin)))
