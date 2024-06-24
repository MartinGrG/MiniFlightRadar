"""Programme de récupération et traitement des bases de données utilisées"""

from opensky_api import OpenSkyApi
import pandas as pd


def vol_aeroport(aeroport, debut, fin):
    """Utitlisation de l'API de OpenSky pour récupérer les informations suivantes:"""
    """'callsign': Numéro donnée à l'appareil par la compagnie aérienne          """
    """'estArrivalAirport': Code de l'aéropot d'arrivée                          """
    """'estDepartureAirport': Code de l'aéroport de départ                       """
    """'icao24': Numéro unique donné à l'appareil par l'OACI                     """
    """'firstSeen': temps en UNIX pour laquelle l'avion a été vu la première fois"""
    """'lasttSeen': temps en UNIX pour laquelle l'avion a été vu la dernière fois"""

    """En argument [début,fin] est l'interval de temps en UNIX (<2h) ...."""
    """aeroport: code OACI de l'aéroport en question"""
    api = OpenSkyApi()
    data_depart = api.get_departures_by_airport(aeroport, debut, fin)
    data_arrivee = api.get_arrivals_by_airport(aeroport, debut, fin)
    # Extraire les attributs des vols et les mettre dans une liste de dictionnaires
    flights_data_depart = []
    flights_data_arrivee = []
    for flight in data_depart:
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

    # Créer un DataFrame à partir de la liste de dictionnaires
    col_names = ['callsign', 'estArrivalAirport', 'estDepartureAirport', 'icao24', 'firstSeen', 'lastSeen']
    flight_depart_df = pd.DataFrame(flights_data_depart, columns=col_names)
    flight_arrivee_df = pd.DataFrame(flights_data_arrivee, columns=col_names)
    flight_df = pd.concat([flight_depart_df, flight_arrivee_df], ignore_index=True)
    return flight_df


def FAA(DF):
    """Chargement et traitement de la base de donnée de la FAA"""
    """Base de donnee master"""
    FAA_df = pd.read_csv('master.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[2, 3, 33])
    FAA_df.rename(columns={'MODE S CODE HEX': 'icao24'}, inplace=True)
    FAA_df.rename(columns={'MFR MDL CODE': 'CODE'}, inplace=True)
    FAA_df.rename(columns={'ENG MFR MDL': 'CODE ENGINE'}, inplace=True)
    FAA_df['icao24'] = FAA_df['icao24'].str.strip()

    """Base de donnee modele"""
    model_df = pd.read_csv('modele.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[0, 2])

    """Base de donnee des moteurs"""
    engine_df = pd.read_csv('engine.csv', sep=',', encoding='utf-8', low_memory=False, usecols=[0, 2])
    engine_df.rename(columns={'CODE': 'CODE ENGINE'}, inplace=True)
    engine_df.rename(columns={'MODEL': 'ENGINE'}, inplace=True)
    DF['icao24'] = DF['icao24'].str.upper()

    engine_df['CODE ENGINE'] = engine_df['CODE ENGINE'].astype(str)
    FAA_df['CODE ENGINE'] = FAA_df['CODE ENGINE'].astype(str)

    merged_df = pd.merge(DF, FAA_df, on='icao24')
    merged_df = pd.merge(merged_df, model_df, on='CODE')
    merged_df = pd.merge(merged_df, engine_df, on='CODE ENGINE')
    merged_df.insert(0, 'index', range(1, len(merged_df) + 1))
    # Sauvegarder le DataFrame dans un fichier CSV
    merged_df.to_csv('flights_data.csv', index=False)
    return merged_df


def airplane_traj(icao24, t):
    api = OpenSkyApi()
    data = api.get_track_by_aircraft(icao24, t)
    return data.path


def sortie(aeroport, temps):
    DB_finale = FAA(vol_aeroport(aeroport, temps, temps+7200))
    for i in range(11):
        DB = FAA(vol_aeroport(aeroport, temps+7200+7200*i, temps+7200+7200*(i+1)))
        DB_finale = pd.concat([DB_finale, DB])

    return DB_finale
