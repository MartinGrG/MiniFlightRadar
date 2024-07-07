"""
Ce script permet d'établir les fonctions nécessaires au calcul de l'empreinte carbone globale d'un vol et de
l'équivalent pour un passager.
"""

from FlightRadar.DataBase.DataBase import engine_emission, aircraft_emission, model_is_present

# Facteurs et constantes
EF = 3.16  # Facteur d’émission
P = 0.538  # Facteur de pré-production
M = 3  # Multiplicateur
AF = 0.00034  # Facteur de l’aéronef
A = 11.68  # Facteaur d'aéroport/infrastructure

# Classes de sièges et multiplicateurs correspondants
SEAT_CLASS = {
    "economy": [1, 1, 1, 4],  # court-courrier, long-courrier, fret, jet privé
    "premium economy": [1, 1.5, 1, 4],
    "affaires": [1.5, 4, 1, 4],
    "première": [1.5, 5, 1, 4]
}


def global_carbon_emissions(duration, uid, engines_nb=1):
    """
    Calcule les émissions globales de CO2 pour un vol donné.

    Cette fonction utilise la durée du vol et les moteurs du modèle d'avion pour estimer les émissions de CO2 en
    utilisant une estimation de la consommation.

    :param float duration: La durée du vol en heures.
    :param str uid: L'identifiant unique du moteur du modèle d'avion.
    :param int engines_nb: Le nombre de moteurs de l'avion (par défaut : 1).

    :return: Les émissions estimées de CO2 en kilogrammes pour le vol spécifié.
    :rtype: float
    """

    # Récupère les facteurs de CO2 pour le moteur déterminé
    engine_info = engine_emission(uid).reset_index(drop=True)

    # Calcule les émissions de carbone globales en utilisant les facteurs et la formule quadratique
    return ((engine_info["Fuel Flow T/O (kg/sec)"][0]*0.3*duration+engine_info["Fuel LTO Cycle (kg)  "][0])*engines_nb
            * (P+EF*M))


def passenger_carbon_emissions(distance, duration, model, uid, engines_nb=1, seat_class="economy"):
    """
    Calcule les émissions de CO2 par passager en fonction de la distance, du modèle d'avion et de la classe de siège.

    :param float distance: La distance en kilomètres.
    :param float duration: La durée du vol en heures.
    :param str model: Le modèle de l'avion.
    :param str uid: L'identifiant unique du moteur du modèle d'avion.
    :param int engines_nb: Le nombre de moteurs de l'avion (par défaut : 1).
    :param str seat_class: La classe de siège du passager (par défaut : "economy").

    :return: Les émissions de CO2 par passager en kilogrammes.
    :rtype: float
    """
    # Vérifie si le modèle donné est dans le dictionnaire des facteurs de CO2 (CO2_factors)
    if not model_is_present(model):
        # Si le modèle n'est pas trouvé, détermine si le vol est court-courrier ou long-courrier
        if distance < 2000:
            model = "Court-courrier"  # Modèle pour vol court-courrier
        else:
            model = "Long-courrier"  # Modèle pour vol long-courrier

    # Récupère les facteurs de CO2 pour le modèle déterminé
    aircraft_info = aircraft_emission(model)

    # Calcule les émissions de CO2 par passager en tenant compte de la classe de siège
    return (global_carbon_emissions(duration, uid, engines_nb)*(1-aircraft_info["CF"][0]) *
            SEAT_CLASS[seat_class][aircraft_info["CW"][0]]/(aircraft_info["S"][0]*aircraft_info["PLF"][0]) +
            AF*distance+A)
